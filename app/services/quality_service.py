from __future__ import annotations

from datetime import datetime, timezone

from ..business_models import QualityCheck


class QualityService:
    """Simple quality-check service for repair photo-based review."""

    def __init__(self) -> None:
        self._checks: dict[str, list[QualityCheck]] = {}

    def add_check(self, repair_id: str, *, result: str, notes: str = "", checked_by: str = "system") -> QualityCheck:
        check = QualityCheck(
            repair_id=repair_id,
            result=result,
            notes=notes,
            checked_by=checked_by,
            created_at=datetime.now(timezone.utc),
        )
        self._checks.setdefault(repair_id, []).append(check)
        return check

    def list_checks(self, repair_id: str) -> list[QualityCheck]:
        return list(self._checks.get(repair_id, []))


__all__ = ["QualityService"]
