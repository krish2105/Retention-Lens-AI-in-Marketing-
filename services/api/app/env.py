"""Shared runtime state for one API process: settings, database, serving stores, limiter."""
from __future__ import annotations

from pathlib import Path

from fastapi import HTTPException

from .db import LOCAL_ORG, Database, now
from .security import RateLimiter
from .settings import Settings
from .store import ServingStore

UPLOAD_ONLY_HINT = "This view is built for the reference dataset only; it is not computed for uploaded data yet"


class Env:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.db = Database(settings.state_db, settings.database_url, settings.db_schema)
        self.reference = ServingStore(settings.serving_dir)
        self.limiter = RateLimiter()
        self._stores: dict[Path, ServingStore] = {}
        with self.db.connect() as db:
            # The single-user local workspace sees the reference dataset until it uploads its own.
            db.execute("INSERT OR IGNORE INTO orgs (id, name, plan, use_sample, created_at) VALUES (?,?,?,?,?)",
                       (LOCAL_ORG, "Local workspace", "pilot", 1, now()))

    def org(self, org_id: str) -> dict:
        rows = self.db.rows("SELECT * FROM orgs WHERE id=?", (org_id,))
        if not rows:
            raise HTTPException(404, "Unknown workspace")
        return rows[0]

    def org_dir(self, org_id: str) -> Path:
        return self.settings.data_dir / org_id

    def dataset_dir(self, org_id: str, dataset_id: str) -> Path:
        return self.org_dir(org_id) / "datasets" / dataset_id

    def dataset_store(self, org_id: str, dataset_id: str) -> ServingStore:
        directory = self.dataset_dir(org_id, dataset_id)
        if directory not in self._stores:
            self._stores[directory] = ServingStore(directory, missing_hint=UPLOAD_ONLY_HINT)
        return self._stores[directory]

    def store_for(self, org_id: str) -> ServingStore:
        """The serving data an org sees: its active upload, else the sample if enabled, else nothing."""
        org = self.org(org_id)
        if org["active_dataset"]:
            return self.dataset_store(org_id, org["active_dataset"])
        if org["use_sample"]:
            return self.reference
        raise HTTPException(409, "No data yet: upload your invoices or load the sample dataset")

    def forget_store(self, directory: Path) -> None:
        self._stores.pop(directory, None)
