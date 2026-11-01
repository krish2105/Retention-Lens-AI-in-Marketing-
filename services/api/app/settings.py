"""Runtime settings, all overridable by environment variables. Secrets come only from the environment."""
from __future__ import annotations

import os
import shlex
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class Settings:
    serving_dir: Path
    state_db: Path
    data_dir: Path
    ollama_url: str
    ollama_model: str
    cors_origins: tuple[str, ...]
    auth_mode: str  # "off" (single local user), "local" (email + password) or "supabase" (Supabase JWT)
    cookie_secure: bool
    supabase_jwt_secret: str
    ml_command: tuple[str, ...]
    admin_token: str
    stripe_secret_key: str
    stripe_webhook_secret: str
    stripe_prices: dict
    public_web_url: str
    holdout_share: float
    queue_size: int


def load_settings() -> Settings:
    state = REPO / "services" / "api" / ".state"
    default_ml = f"uv run --project {shlex.quote(str(REPO / 'ml'))} python -m retentionlens.ingest"
    auth_mode = os.environ.get("RL_AUTH_MODE", "off")
    if auth_mode not in ("off", "local", "supabase"):
        raise ValueError("RL_AUTH_MODE must be off, local or supabase")
    return Settings(
        serving_dir=Path(os.environ.get("RL_SERVING_DIR", REPO / "artefacts" / "serving")),
        state_db=Path(os.environ.get("RL_STATE_DB", state / "retentionlens.sqlite3")),
        data_dir=Path(os.environ.get("RL_DATA_DIR", state / "orgs")),
        ollama_url=os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434"),
        ollama_model=os.environ.get("OLLAMA_MODEL", "qwen2.5:7b"),
        cors_origins=tuple(o.strip() for o in os.environ.get("RL_CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",") if o.strip()),
        auth_mode=auth_mode,
        cookie_secure=os.environ.get("RL_COOKIE_SECURE", "0") == "1",
        supabase_jwt_secret=os.environ.get("SUPABASE_JWT_SECRET", ""),
        ml_command=tuple(shlex.split(os.environ.get("RL_ML_CMD", default_ml))),
        admin_token=os.environ.get("RL_ADMIN_TOKEN", ""),
        stripe_secret_key=os.environ.get("STRIPE_SECRET_KEY", ""),
        stripe_webhook_secret=os.environ.get("STRIPE_WEBHOOK_SECRET", ""),
        stripe_prices={"starter": os.environ.get("STRIPE_PRICE_STARTER", ""), "growth": os.environ.get("STRIPE_PRICE_GROWTH", "")},
        public_web_url=os.environ.get("RL_PUBLIC_WEB_URL", "http://localhost:3000"),
        holdout_share=float(os.environ.get("RL_HOLDOUT_SHARE", "0.2")),
        queue_size=int(os.environ.get("RL_QUEUE_SIZE", "25")),
    )
