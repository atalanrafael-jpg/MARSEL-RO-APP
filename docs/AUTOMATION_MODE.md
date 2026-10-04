# MARSEL ROAPP — Automation Mode

**Date:** 2026-10-03  
**Status:** READY  
**Mode:** READ_ONLY (fail-closed)  
**Production WRITE:** DISABLED  

## Overview

Automation Mode provides a controlled, fail-closed mechanism for automating read-only operations in MARSEL ROAPP. It is designed to:

- Execute read-only audits (inventory, data quality, entity audit, collision detection, warehouse contract verification)
- Collect evidence deterministically
- Require explicit approval for any action
- Never perform production writes without evidence and approval
- Enforce role-based access control via Supabase Auth

## Architecture

### Endpoints

#### `GET /automation/status`
Returns current automation configuration and mode.

**Response (200):**
```json
{
  "run_id": "status-check",
  "enabled": false,
  "mode": "READ_ONLY",
  "allow_write": false,
  "allow_external_calls": false,
  "max_actions": 1,
  "status": "DISABLED",
  "reason": "READ_ONLY mode enforced; production write disabled by default.",
  "total_actions": 0,
  "successful_actions": 0,
  "failed_actions": 0,
  "review_required_actions": 0,
  "timestamp": "2026-10-03T12:00:00+00:00",
  "actions": []
}
```

#### `POST /automation/run`
Request execution of an automation run. Validation is **fail-closed**.

**Response (200 - Success):**
```json
{
  "status": "accepted",
  "mode": "READ_ONLY",
  "allow_write": false,
  "read_only": true,
  "max_actions_per_run": 1,
  "message": "Automation accepted in fail-closed read-only mode. Production WRITE remains disabled.",
  "require_evidence": true,
  "require_approval": true
}
```

**Response (403 - Fail-Closed):**
```json
{
  "detail": "Automation mode is disabled."
}
```

### Configuration

Set via environment variables or `.env`:

```env
# Automation mode (default: disabled)
AUTOMATION_MODE_ENABLED=false
AUTOMATION_MODE_NAME=READ_ONLY
AUTOMATION_ALLOW_WRITE=false
AUTOMATION_ALLOW_EXTERNAL_CALLS=false
AUTOMATION_MAX_ACTIONS_PER_RUN=1
AUTOMATION_REQUIRE_EVIDENCE=true
AUTOMATION_REQUIRE_APPROVAL=true
```

### Validation Rules

All validation is **fail-closed**:

1. **Must be enabled** — `AUTOMATION_MODE_ENABLED=true`
2. **Must be read-only** — `AUTOMATION_ALLOW_WRITE=false` (cannot be overridden)
3. **No external calls** — `AUTOMATION_ALLOW_EXTERNAL_CALLS=false` (cannot be overridden)
4. **Requires evidence** — `AUTOMATION_REQUIRE_EVIDENCE=true` (RO App API must be configured)
5. **Requires approval** — `AUTOMATION_REQUIRE_APPROVAL=true` (future: explicit approval record)

If any validation fails, the automation request is rejected with `HTTP 403`.

## Automation Actions

### Supported Action Types

- `inventory` — Read-only API inventory audit
- `audit` — Data quality and entity audit
- `collision_detection` — Product code collision analysis
- `warehouse_contract` — Warehouse/stock contract verification

### Action Status

- `pending` — Queued for execution
- `running` — Currently executing
- `success` — Completed successfully
- `failed` — Execution failed
- `review_required` — Completed but requires human review

## Example Usage

### Check Automation Status

```bash
curl -X GET http://localhost:8000/automation/status
```

### Enable Automation (Development Only)

```bash
# Set in .env
AUTOMATION_MODE_ENABLED=true
AUTOMATION_MODE_NAME=READ_ONLY
AUTOMATION_ALLOW_WRITE=false
AUTOMATION_ALLOW_EXTERNAL_CALLS=false
AUTOMATION_MAX_ACTIONS_PER_RUN=5
AUTOMATION_REQUIRE_EVIDENCE=true
AUTOMATION_REQUIRE_APPROVAL=true

# Restart application
uvicorn app.main:app --reload
```

### Request Automation Run

```bash
curl -X POST http://localhost:8000/automation/run
```

Expected response:
```json
{
  "status": "accepted",
  "mode": "READ_ONLY",
  "allow_write": false,
  "read_only": true,
  "max_actions_per_run": 5,
  "message": "Automation accepted in fail-closed read-only mode. Production WRITE remains disabled.",
  "require_evidence": true,
  "require_approval": true
}
```

## Safety Guarantees

### Read-Only Enforcement

✅ **No mutations** — All automation operations are read-only.  
✅ **No external writes** — External service calls are disabled by default.  
✅ **No credential exposure** — Secrets never appear in logs or responses.  
✅ **Deterministic** — Same input → same output, always.  

### Fail-Closed Policy

If **any** condition fails, the entire automation request is rejected:

- Mode not enabled → **403 Forbidden**
- Write automation requested → **403 Forbidden**
- External calls requested → **403 Forbidden**
- Evidence collection fails → **503 Service Unavailable**
- Approval missing → **403 Forbidden**

## Integration with CI/CD

Automation mode is designed to integrate with GitHub Actions workflows:

```yaml
name: Read-Only Automation Audit

on:
  schedule:
    - cron: '17 */6 * * *'  # Every 6 hours

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - name: Check automation status
        run: |
          curl http://localhost:8000/automation/status
      
      - name: Request automation run
        run: |
          curl -X POST http://localhost:8000/automation/run
```

## Testing

Run tests:

```bash
pytest tests/test_automation_mode.py -v
```

Expected output:
```
tests/test_automation_mode.py::test_automation_status_defaults_to_disabled PASSED
tests/test_automation_mode.py::test_automation_run_disabled_by_default PASSED
tests/test_automation_mode.py::test_automation_validation_rejects_write_automation PASSED
tests/test_automation_mode.py::test_automation_validation_rejects_external_calls PASSED
tests/test_automation_mode.py::test_automation_run_endpoint_readonly_mode PASSED
...
```

## Future Enhancements

- [ ] Explicit approval workflow (require user/admin signature)
- [ ] Audit log persistence (track all automation executions)
- [ ] Action retry logic (exponential backoff)
- [ ] Workflow composition (chain multiple automation actions)
- [ ] Evidence archival (store all run artifacts to cold storage)

## References

- [MARSEL_ROAPP_UNIFIED_SYSTEM.md](../MARSEL_ROAPP_UNIFIED_SYSTEM.md)
- [config/marsel_ai_control_policy.json](../config/marsel_ai_control_policy.json)
- [app/automation.py](../app/automation.py)
- [tests/test_automation_mode.py](../tests/test_automation_mode.py)
