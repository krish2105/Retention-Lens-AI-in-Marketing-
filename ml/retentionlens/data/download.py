"""Download UCI Online Retail II and record a checksum manifest."""
from __future__ import annotations

import hashlib
import json
import shutil
import urllib.request
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

UCI_URL = "https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip"
LICENCE = "CC BY 4.0"
CITATION = (
    "Chen, D. (2019). Online Retail II [Dataset]. UCI Machine Learning Repository. "
    "https://doi.org/10.24432/C5CG6D"
)
ZIP_NAME = "online_retail_ii.zip"
MANIFEST_NAME = "online_retail_ii.manifest.json"


class ChecksumMismatch(RuntimeError):
    """The downloaded archive does not match the expected SHA-256."""


@dataclass(frozen=True)
class DownloadResult:
    zip_path: Path
    xlsx_path: Path
    zip_sha256: str
    xlsx_sha256: str
    zip_bytes: int
    url: str
    accessed_at: str


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download_dataset(
    dest_dir: Path, url: str = UCI_URL, expected_zip_sha256: str | None = None
) -> DownloadResult:
    dest_dir.mkdir(parents=True, exist_ok=True)
    zip_path = dest_dir / ZIP_NAME
    if not zip_path.exists():
        partial = zip_path.with_suffix(".part")
        with urllib.request.urlopen(url, timeout=180) as response, partial.open("wb") as out:
            shutil.copyfileobj(response, out)
        partial.replace(zip_path)

    zip_sha256 = sha256_file(zip_path)
    if expected_zip_sha256 and zip_sha256 != expected_zip_sha256:
        raise ChecksumMismatch(f"zip sha256 {zip_sha256} != expected {expected_zip_sha256}")

    with zipfile.ZipFile(zip_path) as archive:
        member = next((n for n in archive.namelist() if n.lower().endswith(".xlsx")), None)
        if member is None:
            raise FileNotFoundError(f"no .xlsx file inside {zip_path.name}")
        xlsx_path = dest_dir / Path(member).name  # basename only: no path escape
        if not xlsx_path.exists():
            with archive.open(member) as src, xlsx_path.open("wb") as dst:
                shutil.copyfileobj(src, dst)

    result = DownloadResult(
        zip_path=zip_path,
        xlsx_path=xlsx_path,
        zip_sha256=zip_sha256,
        xlsx_sha256=sha256_file(xlsx_path),
        zip_bytes=zip_path.stat().st_size,
        url=url,
        accessed_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
    )
    manifest = {
        "url": result.url,
        "zip_path": zip_path.name,
        "xlsx_path": xlsx_path.name,
        "zip_sha256": result.zip_sha256,
        "xlsx_sha256": result.xlsx_sha256,
        "zip_bytes": result.zip_bytes,
        "accessed_at": result.accessed_at,
        "licence": LICENCE,
        "citation": CITATION,
    }
    (dest_dir / MANIFEST_NAME).write_text(json.dumps(manifest, indent=2) + "\n")
    return result
