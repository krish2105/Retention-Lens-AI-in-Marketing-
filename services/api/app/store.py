"""Read-only access to the serving files written by `retentionlens.cli serve`."""
from __future__ import annotations

import json
from pathlib import Path

ARTEFACTS = {
    "summary": "summary.json",
    "accounts": "accounts.json",
    "timeline": "timeline.json",
    "cohorts": "cohorts.json",
    "model_eval": "model_eval.json",
    "data_profile": "data_profile.json",
    "sources": "sources.json",
    "segments": "segments.json",
    "galaxy": "galaxy.json",
    "lookalikes": "lookalikes.json",
    "signals": "signals.json",
    "product_lab": "product_lab.json",
}


class NotBuilt(LookupError):
    """The serving file has not been produced yet."""


class ServingStore:
    def __init__(self, directory: Path):
        self.directory = directory
        self._cache: dict[str, tuple[float, object]] = {}

    def get(self, name: str):
        path = self.directory / ARTEFACTS[name]
        if not path.exists():
            raise NotBuilt(f"{path.name} not found; run `uv run python -m retentionlens.cli serve` in ml/")
        mtime = path.stat().st_mtime
        cached = self._cache.get(name)
        if cached is None or cached[0] != mtime:
            self._cache[name] = (mtime, json.loads(path.read_text()))
        return self._cache[name][1]

    def ready(self) -> bool:
        return (self.directory / ARTEFACTS["summary"]).exists()

    def account(self, customer_id: str) -> dict | None:
        index = {a["customer_id"]: a for a in self.get("accounts")}
        return index.get(customer_id)
