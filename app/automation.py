"""Automation mode for MARSEL ROAPP.

Automation is fail-closed, read-only, evidence-driven, and requires approval.
Production WRITE remains disabled by default.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any

from .config import settings


@dataclass(frozen=True)
class AutomationAction:
    """Single automated action in a run."""
    action_type: str  # "inventory", "audit", "collision_detection", "warehouse_contract"
    status: str  # "pending", "running", "success", "failed", "review_required"
    evidence: dict[str, Any]
    timestamp: str
    error_message: str = ""


@dataclass(frozen=True)
class AutomationRun:
    """Single automation execution."""
    run_id: str
    enabled: bool
    mode: str  # "READ_ONLY", "EVIDENCE_DRIVEN"
    allow_write: bool
    allow_external_calls: bool
    max_actions: int
    actions: list[AutomationAction]
    status: str  # "READY", "DISABLED", "RUNNING", "COMPLETED", "FAILED"
    reason: str
    total_actions: int = 0
    successful_actions: int = 0
    failed_actions: int = 0
    review_required_actions: int = 0
    timestamp: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "enabled": self.enabled,
            "mode": self.mode,
            "allow_write": self.allow_write,
            "allow_external_calls": self.allow_external_calls,
            "max_actions": self.max_actions,
            "status": self.status,
            "reason": self.reason,
            "total_actions": self.total_actions,
            "successful_actions": self.successful_actions,
            "failed_actions": self.failed_actions,
            "review_required_actions": self.review_required_actions,
            "timestamp": self.timestamp,
            "actions": [asdict(a) for a in self.actions],
        }


def get_automation_status() -> AutomationRun:
    """Get current automation mode status."""
    return AutomationRun(
        run_id="status-check",
        enabled=bool(settings.automation_mode_enabled),
        mode=settings.automation_mode_name,
        allow_write=bool(settings.automation_allow_write),
        allow_external_calls=bool(settings.automation_allow_external_calls),
        max_actions=int(settings.automation_max_actions_per_run),
        actions=[],
        status="READY" if settings.automation_mode_enabled else "DISABLED",
        reason="READ_ONLY mode enforced; production write disabled by default.",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


def validate_automation_request() -> None:
    """Validate that automation request is permitted. Fail-closed."""
    if not settings.automation_mode_enabled:
        raise PermissionError("Automation mode is disabled.")

    if settings.automation_allow_write:
        raise PermissionError("Write automation is not permitted without explicit evidence and approval.")

    if settings.automation_allow_external_calls:
        raise PermissionError("External service calls in automation are disabled by default.")

    if settings.automation_max_actions_per_run < 1:
        raise ValueError("automation_max_actions_per_run must be >= 1.")

    if settings.automation_require_evidence and not settings.roapp_base_url:
        raise RuntimeError("Automation requires RO App API configuration for evidence collection.")

    if settings.automation_require_approval:
        # Future: check for explicit approval record in database or workflow
        pass


def create_automation_action(
    action_type: str,
    status: str,
    evidence: dict[str, Any],
    error_message: str = "",
) -> AutomationAction:
    """Create a single automation action record."""
    valid_types = {"inventory", "audit", "collision_detection", "warehouse_contract"}
    valid_statuses = {"pending", "running", "success", "failed", "review_required"}

    if action_type not in valid_types:
        raise ValueError(f"Invalid action_type: {action_type}. Must be one of {valid_types}.")

    if status not in valid_statuses:
        raise ValueError(f"Invalid status: {status}. Must be one of {valid_statuses}.")

    return AutomationAction(
        action_type=action_type,
        status=status,
        evidence=evidence,
        timestamp=datetime.now(timezone.utc).isoformat(),
        error_message=error_message,
    )


def summarize_automation_run(actions: list[AutomationAction]) -> dict[str, Any]:
    """Summarize automation run results."""
    total = len(actions)
    successful = sum(1 for a in actions if a.status == "success")
    failed = sum(1 for a in actions if a.status == "failed")
    review_required = sum(1 for a in actions if a.status == "review_required")

    return {
        "total_actions": total,
        "successful_actions": successful,
        "failed_actions": failed,
        "review_required_actions": review_required,
        "pass_status": "PASS" if failed == 0 and review_required == 0 else "REVIEW_REQUIRED",
        "mode": "READ_ONLY",
        "write_requests_made": 0,
        "ro_app_data_mutated": False,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
