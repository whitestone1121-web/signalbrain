#!/usr/bin/env python3
"""Generate a shields.io endpoint JSON from a ledger — the live trust badge.

Usage: python tools/make_badge.py <ledger.jsonl> [window] > badge.json
Honest by construction: the badge shows whatever the gate shows.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from signalbrain.ledger import class_status, load_rows  # noqa: E402

ledger = Path(sys.argv[1])
window = int(sys.argv[2]) if len(sys.argv) > 2 else 10
status = class_status(load_rows(ledger), window=window)
parts = []
any_eligible = False
for name in sorted(status):
    ok = status[name]["status"] == "auto-merge ELIGIBLE"
    any_eligible = any_eligible or ok
    if name in ("bugfix", "tooling"):
        parts.append(f"{name} {'✓' if ok else '✗'}")
print(json.dumps({
    "schemaVersion": 1,
    "label": "earned autonomy",
    "message": " · ".join(parts) or "no track record",
    "color": "brightgreen" if all(s["status"] == "auto-merge ELIGIBLE" for s in status.values())
             else ("yellowgreen" if any_eligible else "red"),
}))
