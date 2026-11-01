"""Operations (R4): request IDs, structured JSON access logs, latency metrics against SLOs,
security headers, a per-IP rate limit and the public status endpoint."""
from __future__ import annotations

import json
import logging
import secrets
import sys
import threading
import time
from collections import defaultdict, deque

import httpx
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from .env import Env

SLO = {"read_p95_ms": 500, "availability": 0.995, "scoring_100k_lines_minutes": 5}
log = logging.getLogger("retentionlens.access")
if not log.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    log.addHandler(handler)
    log.setLevel(logging.INFO)
    log.propagate = False


class Metrics:
    def __init__(self):
        self.started = time.time()
        self.lock = threading.Lock()
        self.latency: dict[str, deque] = defaultdict(lambda: deque(maxlen=2000))
        self.counts: dict[str, int] = defaultdict(int)
        self.errors: dict[str, int] = defaultdict(int)

    def record(self, route: str, ms: float, status: int) -> None:
        with self.lock:
            self.latency[route].append(ms)
            self.counts[route] += 1
            if status >= 500:
                self.errors[route] += 1

    @staticmethod
    def _pct(values: list[float], q: float) -> float:
        ordered = sorted(values)
        return round(ordered[min(len(ordered) - 1, int(q * len(ordered)))], 1)

    def snapshot(self) -> dict:
        with self.lock:
            routes = {r: {"requests": self.counts[r], "errors_5xx": self.errors[r], "p50_ms": self._pct(list(v), 0.5), "p95_ms": self._pct(list(v), 0.95)}
                      for r, v in self.latency.items() if v}
        reads = [r for r in routes if r.startswith("GET ")]
        worst = max((routes[r]["p95_ms"] for r in reads), default=None)
        total = sum(self.counts.values())
        return {"uptime_seconds": int(time.time() - self.started), "requests": total, "errors_5xx": sum(self.errors.values()),
                "worst_read_p95_ms": worst, "slo": SLO, "read_p95_within_slo": None if worst is None else worst <= SLO["read_p95_ms"], "routes": routes}


SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'",
}


def install(app, env: Env, metrics: Metrics) -> None:
    @app.middleware("http")
    async def observe(request: Request, call_next):
        request_id = request.headers.get("x-request-id") or secrets.token_hex(8)
        client = request.client.host if request.client else "unknown"
        if request.url.path.startswith("/api/") and not env.limiter.allow(f"global:{client}", env.settings.rate_limit_per_minute, 60):
            return JSONResponse({"detail": "Too many requests"}, status_code=429, headers={"Retry-After": "60"})
        start = time.perf_counter()
        status = 500
        try:
            response = await call_next(request)
            status = response.status_code
        finally:
            ms = (time.perf_counter() - start) * 1000
            route = request.scope.get("route")
            name = f"{request.method} {getattr(route, 'path', 'unmatched')}"
            metrics.record(name, ms, status)
            log.info(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "request_id": request_id, "method": request.method,
                                 "route": getattr(route, "path", request.url.path), "status": status, "ms": round(ms, 1)}))
        response.headers["X-Request-ID"] = request_id
        if request.url.path.startswith("/api/"):
            for key, value in SECURITY_HEADERS.items():
                response.headers.setdefault(key, value)
        if env.settings.cookie_secure:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        if request.url.path.startswith("/api/auth"):
            response.headers["Cache-Control"] = "no-store"
        return response


def router(env: Env, metrics: Metrics, worker_alive) -> APIRouter:
    api = APIRouter()

    @api.get("/api/metrics")
    def get_metrics():
        return metrics.snapshot()

    @api.get("/api/status")
    def status():
        components = {}
        try:
            with env.db.connect() as db:
                db.execute("SELECT 1").fetchone()
            components["database"] = {"ok": True}
        except Exception as error:
            components["database"] = {"ok": False, "detail": str(error)[:120]}
        components["reference_data"] = {"ok": env.reference.ready()}
        components["scoring_worker"] = {"ok": worker_alive()}
        jobs = env.db.rows("SELECT status, COUNT(*) AS n FROM datasets GROUP BY status")
        components["jobs"] = {"ok": True, "by_status": {r["status"]: r["n"] for r in jobs}}
        try:
            httpx.get(f"{env.settings.ollama_url}/api/tags", timeout=1.0)
            components["local_ai"] = {"ok": True}
        except httpx.HTTPError:
            components["local_ai"] = {"ok": False, "detail": "Not running: drafts fall back to the template"}
        snap = metrics.snapshot()
        core = all(components[c]["ok"] for c in ("database", "scoring_worker"))
        return {"status": "operational" if core else "degraded", "components": components,
                "uptime_seconds": snap["uptime_seconds"], "worst_read_p95_ms": snap["worst_read_p95_ms"], "slo": SLO,
                "auth_mode": env.settings.auth_mode, "version": "0.4.0"}

    return api
