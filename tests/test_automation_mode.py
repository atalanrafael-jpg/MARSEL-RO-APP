import pytest
from fastapi.testclient import TestClient

from app.automation import (
    AutomationAction,
    create_automation_action,
    get_automation_status,
    summarize_automation_run,
    validate_automation_request,
)
from app.config import settings
from app.main import app


def test_automation_status_defaults_to_disabled():
    """Automation should be disabled by default (fail-closed)."""
    status = get_automation_status()
    assert status.enabled is False
    assert status.mode == "READ_ONLY"
    assert status.status == "DISABLED"
    assert status.allow_write is False


def test_automation_status_endpoint():
    """GET /automation/status should return current status."""
    response = TestClient(app).get("/automation/status")
    assert response.status_code == 200
    payload = response.json()
    assert payload["enabled"] is False
    assert payload["mode"] == "READ_ONLY"
    assert payload["status"] == "DISABLED"


def test_automation_run_disabled_by_default():
    """POST /automation/run should reject when disabled."""
    response = TestClient(app).post("/automation/run")
    assert response.status_code == 403
    assert "Automation mode is disabled" in response.json()["detail"]


def test_automation_validation_rejects_write_automation(monkeypatch):
    """Automation validation should reject write requests."""
    monkeypatch.setattr(settings, "automation_mode_enabled", True)
    monkeypatch.setattr(settings, "automation_allow_write", True)
    try:
        with pytest.raises(PermissionError, match="Write automation is not permitted"):
            validate_automation_request()
    finally:
        monkeypatch.setattr(settings, "automation_mode_enabled", False)
        monkeypatch.setattr(settings, "automation_allow_write", False)


def test_automation_validation_rejects_external_calls(monkeypatch):
    """Automation validation should reject external service calls by default."""
    monkeypatch.setattr(settings, "automation_mode_enabled", True)
    monkeypatch.setattr(settings, "automation_allow_write", False)
    monkeypatch.setattr(settings, "automation_allow_external_calls", True)
    try:
        with pytest.raises(PermissionError, match="External service calls"):
            validate_automation_request()
    finally:
        monkeypatch.setattr(settings, "automation_mode_enabled", False)
        monkeypatch.setattr(settings, "automation_allow_external_calls", False)


def test_automation_validation_passes_in_readonly_mode(monkeypatch):
    """Automation validation should pass in read-only mode with proper config."""
    monkeypatch.setattr(settings, "automation_mode_enabled", True)
    monkeypatch.setattr(settings, "automation_allow_write", False)
    monkeypatch.setattr(settings, "automation_allow_external_calls", False)
    monkeypatch.setattr(settings, "automation_max_actions_per_run", 1)
    monkeypatch.setattr(settings, "roapp_base_url", "https://api.roapp.io/v2")
    try:
        validate_automation_request()  # Should not raise
    finally:
        monkeypatch.setattr(settings, "automation_mode_enabled", False)


def test_automation_run_endpoint_readonly_mode(monkeypatch):
    """POST /automation/run should accept and confirm read-only mode."""
    monkeypatch.setattr(settings, "automation_mode_enabled", True)
    monkeypatch.setattr(settings, "automation_allow_write", False)
    monkeypatch.setattr(settings, "automation_allow_external_calls", False)
    monkeypatch.setattr(settings, "automation_max_actions_per_run", 1)
    monkeypatch.setattr(settings, "roapp_base_url", "https://api.roapp.io/v2")
    try:
        response = TestClient(app).post("/automation/run")
        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "accepted"
        assert payload["read_only"] is True
        assert payload["allow_write"] is False
        assert "Production WRITE remains disabled" in payload["message"]
    finally:
        monkeypatch.setattr(settings, "automation_mode_enabled", False)


def test_create_automation_action():
    """Create valid automation action."""
    action = create_automation_action(
        action_type="inventory",
        status="success",
        evidence={"api_coverage": 8, "entities": 5},
    )
    assert action.action_type == "inventory"
    assert action.status == "success"
    assert action.evidence == {"api_coverage": 8, "entities": 5}
    assert action.error_message == ""


def test_create_automation_action_invalid_type():
    """Should reject invalid action type."""
    with pytest.raises(ValueError, match="Invalid action_type"):
        create_automation_action(
            action_type="invalid_action",
            status="success",
            evidence={},
        )


def test_create_automation_action_invalid_status():
    """Should reject invalid status."""
    with pytest.raises(ValueError, match="Invalid status"):
        create_automation_action(
            action_type="inventory",
            status="unknown_status",
            evidence={},
        )


def test_summarize_automation_run_all_success():
    """Summarize run with all successful actions."""
    actions = [
        create_automation_action("inventory", "success", {"count": 100}),
        create_automation_action("audit", "success", {"issues": 0}),
    ]
    summary = summarize_automation_run(actions)
    assert summary["total_actions"] == 2
    assert summary["successful_actions"] == 2
    assert summary["failed_actions"] == 0
    assert summary["review_required_actions"] == 0
    assert summary["pass_status"] == "PASS"
    assert summary["mode"] == "READ_ONLY"
    assert summary["write_requests_made"] == 0
    assert summary["ro_app_data_mutated"] is False


def test_summarize_automation_run_with_failures():
    """Summarize run with some failures."""
    actions = [
        create_automation_action("inventory", "success", {"count": 100}),
        create_automation_action("audit", "failed", {"error": "timeout"}),
        create_automation_action("collision_detection", "review_required", {"findings": 3}),
    ]
    summary = summarize_automation_run(actions)
    assert summary["total_actions"] == 3
    assert summary["successful_actions"] == 1
    assert summary["failed_actions"] == 1
    assert summary["review_required_actions"] == 1
    assert summary["pass_status"] == "REVIEW_REQUIRED"


def test_automation_action_frozen():
    """AutomationAction should be immutable (frozen)."""
    action = create_automation_action("inventory", "success", {})
    with pytest.raises(AttributeError):
        action.action_type = "audit"  # type: ignore


def test_automation_status_as_dict():
    """AutomationRun.as_dict should return serializable dict."""
    status = get_automation_status()
    d = status.as_dict()
    assert isinstance(d, dict)
    assert "run_id" in d
    assert "enabled" in d
    assert "mode" in d
    assert "status" in d
    assert "timestamp" in d
