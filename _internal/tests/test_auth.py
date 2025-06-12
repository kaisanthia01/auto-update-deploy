import os
import json
import pytest
import sys
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import core.auth_service as auth_service
from core.auth_service import AuthService


def test_load_users_missing_file(tmp_path, monkeypatch):
    db_file = tmp_path / "users.json"
    monkeypatch.setattr(auth_service, "USER_DB_FILE", str(db_file))
    service = AuthService()
    assert db_file.exists(), "Database file should be created if missing"
    os.remove(db_file)
    service._load_users()
    assert service.users == {}
    assert db_file.exists(), "Database file recreated when missing"