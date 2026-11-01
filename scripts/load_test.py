"""Load test for the API's read paths against the SLO (p95 < 500 ms for reads).

  services/api/.venv/bin/python scripts/load_test.py --base http://localhost:8001 --users 20 --seconds 30

Simulates reviewers paging through the queue and accounts. Writes reports/load_test.json and .md.
Run it against a single local instance; it is not a test of a hosted deployment.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import random
import statistics
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import httpx

REPO = Path(__file__).resolve().parents[1]
SLO_P95_MS = 500


def pct(values: list[float], q: float) -> float:
    ordered = sorted(values)
    return round(ordered[min(len(ordered) - 1, int(q * len(ordered)))], 1)


async def user(client: httpx.AsyncClient, ids: list[str], until: float, timings, errors, rng: random.Random) -> None:
    routes = [
        ("summary", lambda: "/api/summary"),
        ("queue", lambda: "/api/queue"),
        ("accounts page", lambda: f"/api/accounts?limit=50&offset={rng.randrange(0, 2000, 50)}&sort=value_at_risk_90"),
        ("account detail", lambda: f"/api/accounts/{rng.choice(ids)}"),
        ("account search", lambda: f"/api/accounts?search={rng.choice(['united', '12', 'fra', '17'])}"),
        ("cohorts", lambda: "/api/cohorts"),
        ("segments", lambda: "/api/segments"),
    ]
    while time.perf_counter() < until:
        name, path = rng.choice(routes)
        started = time.perf_counter()
        try:
            response = await client.get(path())
            if response.status_code >= 400:
                errors[name] += 1
        except httpx.HTTPError:
            errors[name] += 1
        timings[name].append((time.perf_counter() - started) * 1000)


async def main(base: str, users: int, seconds: int) -> dict:
    async with httpx.AsyncClient(base_url=base, timeout=10) as client:
        ids = [a["customer_id"] for a in (await client.get("/api/accounts?limit=500")).json()["items"]]
        timings, errors = defaultdict(list), defaultdict(int)
        until = time.perf_counter() + seconds
        await asyncio.gather(*(user(client, ids, until, timings, errors, random.Random(i)) for i in range(users)))
    routes = {name: {"requests": len(v), "errors": errors[name], "p50_ms": pct(v, 0.5), "p95_ms": pct(v, 0.95), "p99_ms": pct(v, 0.99)} for name, v in sorted(timings.items())}
    total = sum(r["requests"] for r in routes.values())
    every = [t for v in timings.values() for t in v]
    return {"at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "base": base, "users": users, "seconds": seconds, "requests": total,
            "throughput_rps": round(total / seconds, 1), "errors": sum(errors.values()), "p50_ms": pct(every, 0.5), "p95_ms": pct(every, 0.95),
            "mean_ms": round(statistics.mean(every), 1), "slo_p95_ms": SLO_P95_MS, "meets_slo": sum(errors.values()) == 0 and all(r["p95_ms"] <= SLO_P95_MS for r in routes.values()), "routes": routes}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="http://localhost:8001")
    parser.add_argument("--users", type=int, default=20)
    parser.add_argument("--seconds", type=int, default=30)
    args = parser.parse_args()
    result = asyncio.run(main(args.base, args.users, args.seconds))
    (REPO / "reports" / "load_test.json").write_text(json.dumps(result, indent=2) + "\n")
    lines = ["# Load test", "", f"{result['at']} · {result['users']} concurrent simulated reviewers for {result['seconds']} s against one local API process "
             f"(uvicorn, 1 worker, SQLite, reference dataset of 5,852 accounts) on a MacBook, with the per-IP rate limit raised because every simulated user shares one address. `scripts/load_test.py`.", "",
             f"- {result['requests']:,} requests, {result['throughput_rps']} per second, {result['errors']} errors",
             f"- All reads p50 {result['p50_ms']} ms, p95 {result['p95_ms']} ms",
             f"- SLO (no errors, every read route p95 under {SLO_P95_MS} ms): **{'met' if result['meets_slo'] else 'NOT met'}**", "",
             "| Route | Requests | Errors | p50 ms | p95 ms | p99 ms |", "|---|---|---|---|---|---|",
             *[f"| {n} | {r['requests']:,} | {r['errors']} | {r['p50_ms']} | {r['p95_ms']} | {r['p99_ms']} |" for n, r in result["routes"].items()], "",
             "Limits: one machine, warm caches, no network latency, no sign-in. A hosted test should be repeated after deployment.", ""]
    (REPO / "reports" / "load_test.md").write_text("\n".join(lines))
    print(json.dumps({k: result[k] for k in ("requests", "throughput_rps", "errors", "p95_ms", "meets_slo")}))
