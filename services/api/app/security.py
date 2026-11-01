"""Security primitives with no third-party dependencies: password hashing, opaque session
tokens, HS256 JWT verification (Supabase), Stripe webhook signatures and a rate limiter."""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import threading
import time
from collections import defaultdict, deque

SCRYPT_N, SCRYPT_R, SCRYPT_P = 2**14, 8, 1
MIN_PASSWORD = 12  # OWASP ASVS L1 2.1.1


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=SCRYPT_N, r=SCRYPT_R, p=SCRYPT_P, dklen=32)
    return f"scrypt${SCRYPT_N}${SCRYPT_R}${SCRYPT_P}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str | None) -> bool:
    if not stored:
        # Spend the same time as a real check so missing accounts are not revealed by timing.
        hashlib.scrypt(password.encode(), salt=b"0" * 16, n=SCRYPT_N, r=SCRYPT_R, p=SCRYPT_P, dklen=32)
        return False
    _, n, r, p, salt, digest = stored.split("$")
    candidate = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=int(n), r=int(r), p=int(p), dklen=32)
    return hmac.compare_digest(candidate.hex(), digest)


def new_token() -> tuple[str, str]:
    """Return (token for the client, sha256 to store). Only the hash is kept server-side."""
    token = secrets.token_urlsafe(32)
    return token, token_hash(token)


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _b64decode(part: str) -> bytes:
    return base64.urlsafe_b64decode(part + "=" * (-len(part) % 4))


class InvalidToken(ValueError):
    pass


def verify_hs256_jwt(token: str, secret: str, audience: str = "authenticated", leeway: int = 30) -> dict:
    """Verify a Supabase access token (HS256, legacy JWT secret). Rejects any other algorithm."""
    try:
        header_b64, payload_b64, signature_b64 = token.split(".")
        header = json.loads(_b64decode(header_b64))
        payload = json.loads(_b64decode(payload_b64))
    except (ValueError, json.JSONDecodeError) as error:
        raise InvalidToken("malformed token") from error
    if header.get("alg") != "HS256" or not secret:
        raise InvalidToken("unsupported algorithm")
    expected = hmac.new(secret.encode(), f"{header_b64}.{payload_b64}".encode(), hashlib.sha256).digest()
    if not hmac.compare_digest(expected, _b64decode(signature_b64)):
        raise InvalidToken("bad signature")
    now = time.time()
    if payload.get("exp", 0) + leeway < now:
        raise InvalidToken("expired")
    aud = payload.get("aud")
    if audience and aud != audience and not (isinstance(aud, list) and audience in aud):
        raise InvalidToken("wrong audience")
    if not payload.get("sub"):
        raise InvalidToken("no subject")
    return payload


def sign_hs256_jwt(payload: dict, secret: str) -> str:
    """Used by tests and local tooling only."""
    def enc(data: dict) -> str:
        return base64.urlsafe_b64encode(json.dumps(data, separators=(",", ":")).encode()).rstrip(b"=").decode()

    head = enc({"alg": "HS256", "typ": "JWT"})
    body = enc(payload)
    sig = base64.urlsafe_b64encode(hmac.new(secret.encode(), f"{head}.{body}".encode(), hashlib.sha256).digest()).rstrip(b"=").decode()
    return f"{head}.{body}.{sig}"


def verify_stripe_signature(payload: bytes, header: str, secret: str, tolerance: int = 300) -> bool:
    """Stripe-Signature: t=timestamp,v1=hex(hmac_sha256(secret, f"{t}.{payload}"))."""
    if not secret or not header:
        return False
    parts = dict(item.split("=", 1) for item in header.split(",") if "=" in item)
    signatures = [v for k, v in (item.split("=", 1) for item in header.split(",") if "=" in item) if k == "v1"]
    try:
        timestamp = int(parts.get("t", "0"))
    except ValueError:
        return False
    if abs(time.time() - timestamp) > tolerance:
        return False
    expected = hmac.new(secret.encode(), f"{timestamp}.".encode() + payload, hashlib.sha256).hexdigest()
    return any(hmac.compare_digest(expected, s) for s in signatures)


class RateLimiter:
    """Sliding-window limit per key, in memory. One API instance only; use Redis when scaling out."""

    def __init__(self):
        self._hits: dict[str, deque] = defaultdict(deque)
        self._lock = threading.Lock()

    def allow(self, key: str, limit: int, window_seconds: int) -> bool:
        now = time.monotonic()
        with self._lock:
            hits = self._hits[key]
            while hits and hits[0] <= now - window_seconds:
                hits.popleft()
            if len(hits) >= limit:
                return False
            hits.append(now)
            return True
