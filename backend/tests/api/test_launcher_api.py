"""Tests for launcher authority API — v1.1.0."""
import os
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture()
def client(tmp_path):
    db_path = str(tmp_path / "test_auth.db")
    os.environ["AUTH_DB_PATH"] = db_path
    with TestClient(app) as c:
        yield c
    os.environ.pop("AUTH_DB_PATH", None)


# ── /api/v1/launcher/status ───────────────────────────────────────────────────

def test_launcher_status_defaults(client, monkeypatch):
    """No env vars set: launched=false, grant_required=false."""
    monkeypatch.delenv("LAUNCHER_GRANT_TOKEN", raising=False)
    monkeypatch.delenv("REQUIRE_LAUNCHER_GRANT", raising=False)
    import app.core.config as cfg
    monkeypatch.setattr(cfg, "LAUNCHER_GRANT_TOKEN", "")
    monkeypatch.setattr(cfg, "REQUIRE_LAUNCHER_GRANT", False)
    import app.api.launcher as launcher_mod
    monkeypatch.setattr(launcher_mod, "LAUNCHER_GRANT_TOKEN", "")
    monkeypatch.setattr(launcher_mod, "REQUIRE_LAUNCHER_GRANT", False)

    res = client.get("/api/v1/launcher/status")
    assert res.status_code == 200
    data = res.json()
    assert data["launched"] is False
    assert data["grant_required"] is False


def test_launcher_status_launched(client, monkeypatch):
    """LAUNCHER_GRANT_TOKEN set: launched=true."""
    import app.api.launcher as launcher_mod
    monkeypatch.setattr(launcher_mod, "LAUNCHER_GRANT_TOKEN", "abc123token")
    monkeypatch.setattr(launcher_mod, "REQUIRE_LAUNCHER_GRANT", False)

    res = client.get("/api/v1/launcher/status")
    assert res.status_code == 200
    data = res.json()
    assert data["launched"] is True
    assert data["grant_required"] is False


def test_launcher_status_grant_required(client, monkeypatch):
    """REQUIRE_LAUNCHER_GRANT=true: grant_required=true."""
    import app.api.launcher as launcher_mod
    monkeypatch.setattr(launcher_mod, "LAUNCHER_GRANT_TOKEN", "")
    monkeypatch.setattr(launcher_mod, "REQUIRE_LAUNCHER_GRANT", True)

    res = client.get("/api/v1/launcher/status")
    assert res.status_code == 200
    data = res.json()
    assert data["launched"] is False
    assert data["grant_required"] is True


def test_launcher_status_launched_and_required(client, monkeypatch):
    """Both set: launched=true, grant_required=true."""
    import app.api.launcher as launcher_mod
    monkeypatch.setattr(launcher_mod, "LAUNCHER_GRANT_TOKEN", "sometoken")
    monkeypatch.setattr(launcher_mod, "REQUIRE_LAUNCHER_GRANT", True)

    res = client.get("/api/v1/launcher/status")
    assert res.status_code == 200
    data = res.json()
    assert data["launched"] is True
    assert data["grant_required"] is True


def test_launcher_status_no_auth_required(client, monkeypatch):
    """Endpoint must be reachable without any auth headers."""
    import app.api.launcher as launcher_mod
    monkeypatch.setattr(launcher_mod, "LAUNCHER_GRANT_TOKEN", "")
    monkeypatch.setattr(launcher_mod, "REQUIRE_LAUNCHER_GRANT", False)

    res = client.get("/api/v1/launcher/status")
    assert res.status_code == 200  # no 401/403


# ── require_launcher_grant gate on operational routes ─────────────────────────

def test_operational_route_blocked_when_grant_required_and_not_launched(client, monkeypatch):
    """REQUIRE_LAUNCHER_GRANT=true + no token → 503 on control plane."""
    import app.core.config as cfg
    monkeypatch.setattr(cfg, "REQUIRE_LAUNCHER_GRANT", True)
    monkeypatch.setattr(cfg, "LAUNCHER_GRANT_TOKEN", "")

    res = client.get("/control-plane")
    assert res.status_code == 503
    assert "launcher" in res.json()["detail"].lower()


def test_operational_route_accessible_when_launched(client, monkeypatch):
    """REQUIRE_LAUNCHER_GRANT=true + token set → gate passes (may still require session auth)."""
    import app.core.config as cfg
    monkeypatch.setattr(cfg, "REQUIRE_LAUNCHER_GRANT", True)
    monkeypatch.setattr(cfg, "LAUNCHER_GRANT_TOKEN", "valid-grant-token")

    res = client.get("/control-plane")
    # Gate passed — 200 (control plane is open after grant passes)
    assert res.status_code != 503


def test_operational_route_accessible_when_grant_not_required(client, monkeypatch):
    """REQUIRE_LAUNCHER_GRANT=false → gate never blocks regardless of token."""
    import app.core.config as cfg
    monkeypatch.setattr(cfg, "REQUIRE_LAUNCHER_GRANT", False)
    monkeypatch.setattr(cfg, "LAUNCHER_GRANT_TOKEN", "")

    res = client.get("/control-plane")
    # Gate passed — not 503
    assert res.status_code != 503
