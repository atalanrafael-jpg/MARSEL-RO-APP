#!/usr/bin/env python3
"""MARSEL release-readiness controller.

Fail-closed controller for the canonical release. It never writes to RO App and
never treats a placeholder or malformed evidence file as production evidence.

Evidence directory is injectable so workflow artifacts can be validated without
copying or mutating repository evidence.
"""
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = Path(os.environ.get("MARSEL_EVIDENCE_DIR", ROOT / "evidence"))
REQUIRED = [
    ".github/workflows/mcp-production.yml",
    "scripts/marsel_canonical_self_check.py",
    "scripts/marsel_production_gate_v1.py",
    "docs/MARSEL-PRODUCTION-GO-LIVE-GATES.md",
    "docs/MARSEL_ROAPP_TASK_REGISTRY.md",
    "SECURITY.md",
]
REQUIRED_EVIDENCE = [
    "backup_evidence.json",
    "restore_evidence.json",
    "wix_roapp_reconciliation.json",
    "marsel-unified-evidence.json",
    "duplicate_reference_evidence.json",
    "write_dry_run.json",
    "idempotency_evidence.json",
    "rollback_evidence.json",
]
MAX_EVIDENCE_AGE_HOURS = 24
SECRET_PATTERN = re.compile(r"(?i)(bearer\s+|sk-[a-z0-9]|api[_-]?key\s*[:=]|password\s*[:=]|secret\s*[:=])")


def fail(msg: str) -> None:
    raise SystemExit(f"RELEASE_READINESS_FAIL: {msg}")


def resolve_evidence_path(name: str) -> Path | None:
    direct = EVIDENCE_DIR / name
    if direct.exists():
        return direct
    # Restore artifacts currently package backup_evidence.json under backup/.
    candidates = list(EVIDENCE_DIR.glob(f"**/{name}"))
    if len(candidates) == 1:
        return candidates[0]
    return None


def validate_evidence(path: Path) -> dict:
    try:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
    except Exception as exc:
        fail(f"evidence_parse_error:{path.name}:{exc}")

    if not isinstance(data, dict):
        fail(f"evidence_document_is_not_object:{path.name}")
    if SECRET_PATTERN.search(raw):
        fail(f"credential_like_material_in_evidence:{path.name}")

    required = {"status", "observed_at", "source"}
    missing = sorted(required - data.keys())
    if missing:
        fail(f"evidence_schema_missing:{path.name}:{','.join(missing)}")
    if data["status"] != "PASS":
        fail(f"evidence_not_pass:{path.name}:{data['status']}")
    if not isinstance(data["source"], str) or not data["source"].strip():
        fail(f"evidence_source_invalid:{path.name}")

    try:
        observed = datetime.fromisoformat(str(data["observed_at"]).replace("Z", "+00:00"))
    except ValueError as exc:
        fail(f"evidence_timestamp_invalid:{path.name}:{exc}")
    if observed.tzinfo is None:
        fail(f"evidence_timestamp_not_timezone_aware:{path.name}")
    age_hours = (datetime.now(timezone.utc) - observed.astimezone(timezone.utc)).total_seconds() / 3600
    if age_hours < -0.05:
        fail(f"evidence_timestamp_in_future:{path.name}")
    if age_hours > MAX_EVIDENCE_AGE_HOURS:
        fail(f"evidence_stale:{path.name}:age_hours={age_hours:.2f}")
    return data


def main() -> int:
    missing = [p for p in REQUIRED if not (ROOT / p).exists()]
    if missing:
        fail("missing_required_controls=" + ",".join(missing))

    gate = (ROOT / "scripts/marsel_production_gate_v1.py").read_text(encoding="utf-8")
    workflow = (ROOT / ".github/workflows/mcp-production.yml").read_text(encoding="utf-8")
    if "MARSEL_WRITE_APPROVED" not in gate or "fail(\"write_approval_is_not_authorized_by_automated_gate\")" not in gate:
        fail("production_write_fail_closed_control_missing")
    if "pytest" not in workflow or "pip-audit" not in workflow:
        fail("production_ci_controls_missing")

    resolved = {name: resolve_evidence_path(name) for name in REQUIRED_EVIDENCE}
    absent = [name for name, path in resolved.items() if path is None]
    print("MARSEL_RELEASE_READINESS=FAIL_CLOSED")
    print("PRODUCTION_WRITE_AUTHORIZED=false")
    print("REPOSITORY_CONTROLS=PASS")
    print("EVIDENCE_DIR=" + str(EVIDENCE_DIR))
    if absent:
        print("EXTERNAL_EVIDENCE=INCOMPLETE")
        print("MISSING_EVIDENCE=" + ",".join(absent))
        print("RESULT=NOT_PRODUCTION_READY")
        return 2

    for name, path in resolved.items():
        assert path is not None
        validate_evidence(path)

    print("EXTERNAL_EVIDENCE=PRESENT_AND_VALID")
    print("RESULT=RUN_PRODUCTION_GATE_FOR_FINAL_DECISION")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
