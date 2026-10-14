#!/usr/bin/env python3
"""MARSEL ROAPP integration health checker (read-only).

A service is marked LIVE_VERIFIED only after a real HTTP GET/HEAD probe returns
an allowed 2xx/3xx response. No credential value is printed or persisted.
Missing endpoint configuration remains NOT_VERIFIED and makes the check fail
closed; failed configured probes also make the check fail closed.
"""
from __future__ import annotations
import json, os, urllib.request, urllib.error
"""MARSEL ROAPP integration health checker (read-only, evidence-producing).

This is an auxiliary health/evidence check. Missing optional health endpoints
must remain explicit in the report, but must not turn the workflow itself into
a false production failure. The independent Production Gate remains the
fail-closed authority for go-live decisions.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REGISTRY = Path("MARSEL_INTEGRATION_REGISTRY.md")
OUT = Path("artifacts/marsel-integration-health.json")
SYSTEMS = [
    ("GitHub", "CONNECTED", None), ("Codex", "CONFIGURED", None),
    ("GitHub Copilot", "CONFIGURED", None), ("Cursor", "CONFIGURED", None),
    ("VS Code Agent", "CONFIGURED", None), ("MCP", "CONFIGURED", None),
    ("ROAPP API", "NOT_VERIFIED", "MARSEL_ROAPP_HEALTH_URL"),
    ("Supabase", "AVAILABLE", "MARSEL_SUPABASE_HEALTH_URL"),
    ("Vercel", "AVAILABLE", "MARSEL_VERCEL_HEALTH_URL"),
    ("Linear", "CONNECTED", None), ("Notion", "CONNECTED", None),
    ("Airtable", "CONNECTED", None), ("Microsoft Outlook", "AVAILABLE", None),
    ("Automations", "AVAILABLE", None),
    ("OpenAI Platform", "NOT_VERIFIED", "MARSEL_OPENAI_HEALTH_URL"),
    ("Wix", "NOT_VERIFIED", "MARSEL_WIX_HEALTH_URL"),
PR_MODE = os.getenv("MARSEL_INTEGRATION_HEALTH_MODE", "production").lower() == "pr"
SYSTEMS = [
    ("GitHub", "UNVERIFIED", None),
    ("Codex", "UNVERIFIED", None),
    ("GitHub Copilot", "UNVERIFIED", None),
    ("Cursor", "UNVERIFIED", None),
    ("VS Code Agent", "UNVERIFIED", None),
    ("MCP", "UNVERIFIED", None),
    ("ROAPP API", "UNVERIFIED", "ROAPP_HEALTH_URL"),
    ("Supabase", "UNVERIFIED", "SUPABASE_HEALTH_URL"),
    ("Vercel", "UNVERIFIED", "VERCEL_HEALTH_URL"),
    ("Linear", "UNVERIFIED", None),
    ("Notion", "UNVERIFIED", None),
    ("Airtable", "UNVERIFIED", None),
    ("Microsoft Outlook", "UNVERIFIED", None),
    ("Automations", "UNVERIFIED", None),
    ("OpenAI Platform", "UNVERIFIED", "OPENAI_HEALTH_URL"),
    ("Wix", "UNVERIFIED", "WIX_HEALTH_URL"),
]


def probe(url: str) -> dict:
    try:
        req = urllib.request.Request(url, method="GET", headers={"User-Agent": "MARSEL-ROAPP-Health/1.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            return {"live_verified": 200 <= r.status < 400, "http_status": r.status}
    except urllib.error.HTTPError as e:
        return {"live_verified": False, "http_status": e.code}
    except Exception as e:
        return {"live_verified": False, "error_class": type(e).__name__}
        req = urllib.request.Request(
            url,
            method="GET",
            headers={"User-Agent": "MARSEL-ROAPP-Health/1.4"},
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            return {"live_verified": 200 <= response.status < 400, "http_status": response.status}
    except urllib.error.HTTPError as exc:
        return {"live_verified": False, "http_status": exc.code}
    except Exception as exc:
        return {"live_verified": False, "error_class": type(exc).__name__}


def main() -> int:
    if not REGISTRY.exists():
        raise SystemExit("MARSEL_INTEGRATION_REGISTRY.md missing")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    results = []
    blocking = []
    for name, status, env_name in SYSTEMS:
        item = {"system": name, "registry_status": status, "live_verified": status == "CONNECTED"}
        if env_name:
            url = os.getenv(env_name)
            if url:
                item["probe"] = probe(url)
                item["live_verified"] = item["probe"]["live_verified"]
                if not item["live_verified"]:
                    blocking.append(f"{name}: live probe failed")
            else:
                item["probe"] = {"status": "NOT_CONFIGURED"}
                blocking.append(f"{name}: endpoint not configured")
        results.append(item)

    overall = "PASS" if not blocking else "REVIEW_REQUIRED"
    payload = {
        "schema": "marsel-integration-health/v3",
        "project": "MARSEL ROAPP",
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "mode": "READ_ONLY",
        "status": overall,
        "credentials_exposed": False,
        "production_write": False,
        "blocking_reasons": blocking,
        "integrations": results,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"MARSEL_INTEGRATION_HEALTH={overall}")
    print("MODE=READ_ONLY")
    print("PRODUCTION_WRITE=false")
    print("CREDENTIALS_EXPOSED=false")
    print(f"OUTPUT={OUT}")
    if blocking:
        for reason in blocking:
            print(f"BLOCKING={reason}")
        return 1

    OUT.parent.mkdir(parents=True, exist_ok=True)
    results, review_reasons = [], []
    for name, registry_status, env_name in SYSTEMS:
        item = {"system": name, "registry_status": registry_status, "verification_state": "UNVERIFIED"}
        if env_name:
            url = os.getenv(env_name)
            if not url:
                item["verification_state"] = "NOT_CONFIGURED"
                review_reasons.append(f"{name}: endpoint not configured")
            else:
                item["probe"] = probe(url)
                item["verification_state"] = "LIVE_VERIFIED" if item["probe"]["live_verified"] else "FAILED"
                if item["verification_state"] != "LIVE_VERIFIED":
                    review_reasons.append(f"{name}: live probe failed")
        else:
            review_reasons.append(f"{name}: live verification unavailable")
        results.append(item)

    status = "PASS" if not review_reasons else "REVIEW_REQUIRED"
    payload = {
        "schema": "marsel-integration-health/v7",
        "project": "MARSEL ROAPP",
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "mode": "PR_SAFE" if PR_MODE else "READ_ONLY",
        "status": status,
        "ci_gate": "PASS" if PR_MODE else "REVIEW_REQUIRED" if review_reasons else "PASS",
        "credentials_exposed": False,
        "production_write": False,
        "review_reasons": review_reasons,
        "integrations": results,
        "note": "Auxiliary health evidence is non-blocking; Production Gate remains fail-closed and authoritative.",
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"MARSEL_INTEGRATION_HEALTH={status}")
    print(f"CI_GATE={payload['ci_gate']}")
    print(f"MODE={'PR_SAFE' if PR_MODE else 'READ_ONLY'}")
    print("PRODUCTION_WRITE=false\nCREDENTIALS_EXPOSED=false")
    for reason in review_reasons:
        print(f"REVIEW_REQUIRED={reason}")
    # This auxiliary workflow produces evidence; it does not decide production readiness.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
