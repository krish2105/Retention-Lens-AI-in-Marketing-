import os
import tempfile
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def client(monkeypatch,tmp_path):
    monkeypatch.setenv('DEMO_DB_PATH',str(tmp_path/'test.sqlite3'))
    # main.STATE is resolved at import, override it safely per test
    import app.main as mod
    monkeypatch.setattr(mod,'STATE',tmp_path/'test.sqlite3')
    return TestClient(mod.app)
