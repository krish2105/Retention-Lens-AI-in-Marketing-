"""Runtime settings, all overridable by environment variables."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class Settings:
    serving_dir: Path
    state_db: Path
    ollama_url: str
    ollama_model: str
    cors_origins: tuple[str, ...]


def load_settings() -> Settings:
    return Settings(
        serving_dir=Path(os.environ.get("RL_SERVING_DIR", REPO / "artefacts" / "serving")),
        state_db=Path(os.environ.get("RL_STATE_DB", REPO / "services" / "api" / ".state" / "retentionlens.sqlite3")),
        ollama_url=os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434"),
        ollama_model=os.environ.get("OLLAMA_MODEL", "qwen2.5:7b"),
        cors_origins=tuple(os.environ.get("RL_CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")),
    )
