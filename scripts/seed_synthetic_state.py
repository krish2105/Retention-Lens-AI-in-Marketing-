"""Fill a scratch API database with SYNTHETIC workspaces, users, reviews, drafts, labels, queue outcomes
and waitlist rows, through the real API, so restore drills and load tests run on realistic data.

  services/api/.venv/bin/python scripts/seed_synthetic_state.py --db /tmp/rl-drill/state.sqlite3

Never point it at a database holding real customer data.
"""
from __future__ import annotations

import argparse
import os
import random
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def main(db: Path, orgs: int, reviews_per_org: int) -> None:
    os.environ.update({"RL_STATE_DB": str(db), "RL_DB_SCHEMA": os.environ.get("RL_DB_SCHEMA", "seeded"), "RL_DATA_DIR": str(db.parent / "orgs"), "RL_AUTH_MODE": "local",
                       "RL_BACKUP_HOURS": "0", "RL_RATE_LIMIT_PER_MIN": "1000000", "OLLAMA_URL": "http://127.0.0.1:9"})
    sys.path.insert(0, str(REPO / "services" / "api"))
    from fastapi.testclient import TestClient

    import app.main as main

    main.env.limiter.allow = lambda *a, **k: True  # seeding is not an attack
    rng = random.Random(11)
    for o in range(orgs):
        client = TestClient(main.app)
        token = client.post("/api/auth/signup", json={"email": f"owner{o}@synthetic.example", "name": f"Synthetic Owner {o}",
                                                    "password": f"Synthetic-pass-{o}-xyz", "workspace": f"Synthetic Wholesaler {o}"}).json()["token"]
        client.headers["Authorization"] = f"Bearer {token}"
        client.post("/api/org/sample", json={"enabled": True})
        for r in range(2):
            client.post("/api/org/invites", json={"email": f"rev{o}{r}@synthetic.example", "role": "reviewer"})
        ids = [a["customer_id"] for a in client.get("/api/accounts?limit=300").json()["items"]]
        client.get("/api/queue")
        for _ in range(reviews_per_org):
            client.post(f"/api/accounts/{rng.choice(ids)}/reviews", json={"decision": rng.choice(["contact", "keep_watching", "no_action"]), "note": "SYNTHETIC seed review"})
        for i in range(10):
            draft = client.post("/api/drafts", json={"customer_id": rng.choice(ids), "tone": rng.choice(["warm", "brief"])}).json()
            client.post(f"/api/drafts/{draft['id']}/label", json={"label": rng.choice(["pass", "revise"]), "note": "SYNTHETIC"})
            if i % 2 == 0:
                client.post(f"/api/drafts/{draft['id']}/decision", headers={"Idempotency-Key": f"seed-{o}-{i}-key"},
                            json={"decision": "approve", "recipient_type": "company", "consent_basis": "legitimate_interest_b2b"})
    anon = TestClient(main.app)
    for w in range(40):
        anon.post("/api/waitlist", json={"email": f"lead{w}@synthetic.example", "company": "Synthetic Co", "role": "Owner", "accounts_band": "200_1000", "consent": True})
    target = f"Postgres schema {os.environ['RL_DB_SCHEMA']}" if os.environ.get("RL_DATABASE_URL") else str(db)
    print(f"seeded {orgs} synthetic workspaces into {target}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--orgs", type=int, default=5)
    parser.add_argument("--reviews", type=int, default=200)
    args = parser.parse_args()
    if args.db.exists() and not os.environ.get("RL_DATABASE_URL"):
        sys.exit(f"{args.db} exists; use a new scratch path")
    args.db.parent.mkdir(parents=True, exist_ok=True)
    main(args.db, args.orgs, args.reviews)
