"""Self-serve import (R2): upload -> map columns -> validate -> background scoring job.

The ML work runs in a separate process (`python -m retentionlens.ingest`), so the API stays
light and a crash in model fitting cannot take the API down. Job state lives in the database,
so jobs that were queued or running when the API stopped are picked up again on start.
"""
from __future__ import annotations

import hashlib
import json
import math
import queue
import secrets
import shutil
import subprocess
import threading
from pathlib import Path
from typing import Callable, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field

from .billing import PLANS
from .db import now
from .env import Env
from .tenancy import Ctx

MAX_BYTES = 50 * 1024 * 1024
ALLOWED = {".csv", ".txt", ".tsv", ".xlsx", ".xlsm"}
MAX_ATTEMPTS = 2


class JobFailed(RuntimeError):
    def __init__(self, message: str, retryable: bool):
        super().__init__(message)
        self.retryable = retryable


class SubprocessRunner:
    """Runs the ML ingest CLI and reads its JSON-lines output."""

    def __init__(self, command: tuple[str, ...]):
        self.command = list(command)

    def _run(self, args: list[str], on_progress: Callable[[str, int], None] | None = None, timeout: int = 120) -> dict:
        try:
            process = subprocess.Popen(self.command + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        except OSError as error:
            raise JobFailed(f"Could not start the scoring process: {error}", retryable=False) from error
        result, failure = None, None
        timer = threading.Timer(timeout, process.kill)
        timer.start()
        try:
            for line in process.stdout:
                try:
                    message = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if "stage" in message and on_progress:
                    on_progress(message["stage"], int(message["pct"]))
                result = message.get("result", result)
                failure = message.get("error", failure)
            stderr = process.stderr.read()
            code = process.wait()
        finally:
            timer.cancel()
        if failure:
            raise JobFailed(failure, retryable=False)
        if code != 0 or result is None:
            tail = stderr.strip().splitlines()[-1:] if stderr else []
            raise JobFailed(f"Scoring process stopped (exit {code}) {' '.join(tail)}".strip(), retryable=True)
        return result

    def inspect(self, path: Path) -> dict:
        return self._run(["inspect", str(path)])

    def validate(self, path: Path, mapping: dict, date_order: str) -> dict:
        return self._run(["validate", str(path), "--mapping", json.dumps(mapping), "--date-order", date_order])

    def score(self, path: Path, mapping: dict, date_order: str, out: Path, on_progress) -> dict:
        return self._run(["score", str(path), "--mapping", json.dumps(mapping), "--date-order", date_order, "--out", str(out)], on_progress, timeout=1800)


def psi(reference: list[float], current: list[float], bins: int = 10) -> float | None:
    """Population stability index of two score distributions on fixed [0,1] bins."""
    if len(reference) < 20 or len(current) < 20:
        return None
    def shares(values: list[float]) -> list[float]:
        counts = [0] * bins
        for v in values:
            counts[min(int(max(v, 0) * bins), bins - 1)] += 1
        return [max(c / len(values), 1e-4) for c in counts]

    ref, cur = shares(reference), shares(current)
    return round(sum((c - r) * math.log(c / r) for r, c in zip(ref, cur)), 4)


class MappingIn(BaseModel):
    mapping: dict[str, str | None]
    date_order: Literal["auto", "dayfirst", "monthfirst"] = "auto"


class Worker:
    """One background thread; jobs are dataset ids. Durable because state is in the database."""

    def __init__(self, env: Env, runner, on_ready: Callable[[str, str], None]):
        self.env, self.runner, self.on_ready = env, runner, on_ready
        self.jobs: queue.Queue[str] = queue.Queue()
        self.thread = threading.Thread(target=self._loop, name="scoring-worker", daemon=True)
        self.thread.start()
        for row in env.db.rows("SELECT id FROM datasets WHERE status IN ('queued', 'scoring') ORDER BY updated_at"):
            self.update(row["id"], status="queued", stage="requeued after restart", pct=0)
            self.jobs.put(row["id"])

    def update(self, dataset_id: str, **fields) -> None:
        fields["updated_at"] = now()
        assignments = ", ".join(f"{k}=?" for k in fields)
        with self.env.db.connect() as db:
            db.execute(f"UPDATE datasets SET {assignments} WHERE id=?", (*fields.values(), dataset_id))

    def submit(self, dataset_id: str) -> None:
        self.jobs.put(dataset_id)

    def _loop(self) -> None:
        while True:
            dataset_id = self.jobs.get()
            try:
                self.run(dataset_id)
            except Exception as error:  # never let one job kill the worker
                self.update(dataset_id, status="failed", error=f"Unexpected error: {error}")
            finally:
                self.jobs.task_done()

    def run(self, dataset_id: str) -> None:
        rows = self.env.db.rows("SELECT * FROM datasets WHERE id=?", (dataset_id,))
        if not rows or rows[0]["status"] != "queued":
            return
        ds = rows[0]
        out = self.env.dataset_dir(ds["org_id"], ds["id"])
        upload = self._upload_path(ds)
        for attempt in range(ds["attempts"] + 1, MAX_ATTEMPTS + 1):
            self.update(dataset_id, status="scoring", stage="starting", pct=1, attempts=attempt, error=None)
            try:
                summary = self.runner.score(upload, json.loads(ds["mapping"]), ds["date_order"], out,
                                            lambda stage, pct: self.update(dataset_id, stage=stage, pct=pct))
            except JobFailed as error:
                if error.retryable and attempt < MAX_ATTEMPTS:
                    continue
                self.update(dataset_id, status="failed", stage="failed", error=str(error))
                return
            summary["drift"] = self._drift(ds["org_id"], out)
            self.update(dataset_id, status="ready", stage="done", pct=100, summary=json.dumps(summary))
            self.env.forget_store(out)
            self.on_ready(ds["org_id"], dataset_id)
            return

    def _upload_path(self, ds: dict) -> Path:
        return self.env.org_dir(ds["org_id"]) / "uploads" / f"{ds['id']}{Path(ds['filename']).suffix.lower()}"

    def _drift(self, org_id: str, out: Path) -> dict:
        """Compare this upload's lapse scores with the workspace's previous active dataset."""
        org = self.env.org(org_id)
        try:
            current = [a["p_lapse"] for a in json.loads((out / "accounts.json").read_text())]
            if not org["active_dataset"]:
                return {"psi": None, "against": None, "note": "First dataset in this workspace: nothing to compare with"}
            previous = [a["p_lapse"] for a in self.env.dataset_store(org_id, org["active_dataset"]).get("accounts")]
        except Exception:
            return {"psi": None, "against": None, "note": "Previous scores not available"}
        value = psi(previous, current)
        level = None if value is None else ("stable" if value < 0.1 else "moderate shift" if value < 0.25 else "large shift: check the data before acting")
        return {"psi": value, "against": org["active_dataset"], "note": level}


def router(env: Env, ctx, require, runner, worker: Worker) -> APIRouter:
    api = APIRouter()

    def get_dataset(context: Ctx, dataset_id: str) -> dict:
        rows = env.db.rows("SELECT * FROM datasets WHERE id=? AND org_id=?", (dataset_id, context.org_id))
        if not rows:
            raise HTTPException(404, "Unknown dataset")
        row = rows[0]
        for field in ("mapping", "inspect", "validation", "summary"):
            row[field] = json.loads(row[field]) if row[field] else None
        return row

    @api.post("/api/datasets")
    async def upload(request: Request, filename: str = Query(..., min_length=1, max_length=200), context: Ctx = Depends(require("reviewer"))):
        suffix = Path(filename).suffix.lower()
        if suffix not in ALLOWED:
            raise HTTPException(415, "Upload a .csv or .xlsx file")
        if not env.limiter.allow(f"upload:{context.org_id}", 20, 3600):
            raise HTTPException(429, "Upload limit reached for this hour")
        declared = int(request.headers.get("content-length") or 0)
        if declared > MAX_BYTES:
            raise HTTPException(413, "Files up to 50 MB are supported")
        body = bytearray()
        async for chunk in request.stream():
            body.extend(chunk)
            if len(body) > MAX_BYTES:
                raise HTTPException(413, "Files up to 50 MB are supported")
        if not body:
            raise HTTPException(422, "The file is empty")
        digest = hashlib.sha256(body).hexdigest()
        # Idempotent import: the same file uploaded twice to one workspace is one dataset.
        existing = env.db.rows("SELECT id FROM datasets WHERE org_id=? AND sha256=?", (context.org_id, digest))
        if existing:
            return {**get_dataset(context, existing[0]["id"]), "duplicate": True}
        dataset_id = "d_" + secrets.token_hex(8)
        uploads = env.org_dir(context.org_id) / "uploads"
        uploads.mkdir(parents=True, exist_ok=True)
        path = uploads / f"{dataset_id}{suffix}"
        path.write_bytes(bytes(body))
        try:
            inspected = runner.inspect(path)
        except JobFailed as error:
            path.unlink(missing_ok=True)
            raise HTTPException(422, str(error)) from error
        safe_name = Path(filename).name[:200]
        with env.db.connect() as db:
            db.execute(
                "INSERT INTO datasets (id, org_id, filename, sha256, bytes, status, mapping, inspect, created_by, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (dataset_id, context.org_id, safe_name, digest, len(body), "uploaded", json.dumps(inspected["suggested_mapping"]), json.dumps(inspected), context.email, now(), now()),
            )
            env.db.audit(db, context.email, "dataset_uploaded", f"dataset:{dataset_id}", {"filename": safe_name, "bytes": len(body), "sha256": digest}, context.org_id)
        return {**get_dataset(context, dataset_id), "duplicate": False}

    @api.get("/api/datasets")
    def list_datasets(context: Ctx = Depends(ctx)):
        rows = env.db.rows("SELECT id, filename, bytes, status, stage, pct, error, created_by, created_at, updated_at FROM datasets WHERE org_id=? ORDER BY created_at DESC", (context.org_id,))
        active = env.org(context.org_id)["active_dataset"]
        return [{**r, "active": r["id"] == active} for r in rows]

    @api.get("/api/datasets/{dataset_id}")
    def dataset(dataset_id: str, context: Ctx = Depends(ctx)):
        row = get_dataset(context, dataset_id)
        return {**row, "active": env.org(context.org_id)["active_dataset"] == dataset_id}

    @api.post("/api/datasets/{dataset_id}/validate")
    def validate(dataset_id: str, body: MappingIn, context: Ctx = Depends(require("reviewer"))):
        ds = get_dataset(context, dataset_id)
        if ds["status"] in ("queued", "scoring"):
            raise HTTPException(409, "This dataset is being scored")
        try:
            report = runner.validate(worker._upload_path(ds), body.mapping, body.date_order)
        except JobFailed as error:
            raise HTTPException(422, str(error)) from error
        status = "validated" if report["can_score"] else "needs_fixes"
        worker.update(dataset_id, status=status, mapping=json.dumps(body.mapping), date_order=body.date_order, validation=json.dumps(report), error=None)
        return get_dataset(context, dataset_id)

    @api.post("/api/datasets/{dataset_id}/score")
    def score(dataset_id: str, context: Ctx = Depends(require("reviewer"))):
        ds = get_dataset(context, dataset_id)
        if ds["status"] in ("queued", "scoring"):
            return ds
        if ds["status"] not in ("validated", "failed", "ready"):
            raise HTTPException(409, "Check the column mapping before scoring")
        plan = PLANS[env.org(context.org_id)["plan"]]
        customers = (ds["validation"] or {}).get("customers", 0)
        if customers > plan["max_accounts"]:
            raise HTTPException(402, f"This file has {customers:,} accounts; the {plan['name']} plan covers up to {plan['max_accounts']:,}")
        worker.update(dataset_id, status="queued", stage="queued", pct=0, attempts=0, error=None)
        with env.db.connect() as db:
            env.db.audit(db, context.email, "dataset_scoring_queued", f"dataset:{dataset_id}", {"customers": customers}, context.org_id)
        worker.submit(dataset_id)
        return get_dataset(context, dataset_id)

    @api.post("/api/datasets/{dataset_id}/activate")
    def activate(dataset_id: str, context: Ctx = Depends(require("reviewer"))):
        if get_dataset(context, dataset_id)["status"] != "ready":
            raise HTTPException(409, "Only a scored dataset can be made active")
        with env.db.connect() as db:
            db.execute("UPDATE orgs SET active_dataset=? WHERE id=?", (dataset_id, context.org_id))
            env.db.audit(db, context.email, "dataset_activated", f"dataset:{dataset_id}", {}, context.org_id)
        return {"ok": True}

    @api.post("/api/datasets/{dataset_id}/delete")
    def delete(dataset_id: str, context: Ctx = Depends(require("owner"))):
        ds = get_dataset(context, dataset_id)
        if ds["status"] in ("queued", "scoring"):
            raise HTTPException(409, "Wait for scoring to finish before deleting")
        directory = env.dataset_dir(context.org_id, dataset_id)
        shutil.rmtree(directory, ignore_errors=True)
        env.forget_store(directory)
        worker._upload_path(ds).unlink(missing_ok=True)
        with env.db.connect() as db:
            db.execute("DELETE FROM datasets WHERE id=? AND org_id=?", (dataset_id, context.org_id))
            db.execute("UPDATE orgs SET active_dataset=NULL WHERE id=? AND active_dataset=?", (context.org_id, dataset_id))
            env.db.audit(db, context.email, "dataset_deleted", f"dataset:{dataset_id}", {"filename": ds["filename"]}, context.org_id)
        return {"ok": True}

    return api
