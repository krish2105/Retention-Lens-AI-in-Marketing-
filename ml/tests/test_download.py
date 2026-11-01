import json
import zipfile

import pytest

from retentionlens.data.download import ChecksumMismatch, download_dataset, sha256_file


def make_zip(path, members):
    with zipfile.ZipFile(path, "w") as z:
        for name, data in members.items():
            z.writestr(name, data)
    return path


def test_downloads_extracts_and_writes_manifest(tmp_path):
    src = make_zip(tmp_path / "src.zip", {"online_retail_II.xlsx": b"fake-xlsx"})
    dest = tmp_path / "raw"
    result = download_dataset(dest, url=src.as_uri())
    assert result.xlsx_path.read_bytes() == b"fake-xlsx"
    assert result.zip_sha256 == sha256_file(src)
    manifest = json.loads((dest / "online_retail_ii.manifest.json").read_text())
    assert manifest["licence"] == "CC BY 4.0"
    assert manifest["zip_sha256"] == result.zip_sha256
    assert manifest["xlsx_path"] == "online_retail_II.xlsx"


def test_checksum_mismatch_raises(tmp_path):
    src = make_zip(tmp_path / "src.zip", {"online_retail_II.xlsx": b"x"})
    with pytest.raises(ChecksumMismatch):
        download_dataset(tmp_path / "raw", url=src.as_uri(), expected_zip_sha256="0" * 64)


def test_zip_without_xlsx_raises(tmp_path):
    src = make_zip(tmp_path / "src.zip", {"readme.txt": b"no data"})
    with pytest.raises(FileNotFoundError):
        download_dataset(tmp_path / "raw", url=src.as_uri())


def test_member_path_cannot_escape_dest(tmp_path):
    src = make_zip(tmp_path / "src.zip", {"../../evil.xlsx": b"x"})
    result = download_dataset(tmp_path / "raw", url=src.as_uri())
    assert result.xlsx_path.parent == tmp_path / "raw"
