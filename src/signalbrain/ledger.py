"""Calibration ledger math — the trust core.

Extracted from neural-chat-v3 `calibration_ledger_core` (incident-tested through
2026-07; see docs/RECEIPT_SPEC.md §6). Pure functions over ledger rows; no I/O
beyond `load_rows`.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

HIGH_CONFIDENCE_THRESHOLD = 0.85
DEFAULT_MIN_HIT_RATE = 0.95
MIN_TRACK_RECORD = 10
DEFAULT_RECENCY_WINDOW = 20
SCORED_BY_MEASURED = "measured"
CLAIM_KIND_IMPROVEMENT = "improvement_claim"
CLAIM_KIND_INVARIANT_PIN = "invariant_pin"
GOODHART_EXCLUDED_RECEIPT_MARKERS = (
    "trust-pin",
    "trust_pin",
)


def receipt_id(row: dict[str, Any]) -> str:
    return str(row.get("receipt_id") or row.get("claim") or "")


def is_goodhart_excluded_receipt_id(receipt_id_value: str) -> bool:
    rid = receipt_id_value.strip().lower()
    if not rid:
        return False
    return any(marker in rid for marker in GOODHART_EXCLUDED_RECEIPT_MARKERS)


def claim_kind(row: dict[str, Any]) -> str:
    raw = str(row.get("claim_kind") or "").strip()
    if raw:
        return raw
    if is_goodhart_excluded_receipt_id(receipt_id(row)):
        return CLAIM_KIND_INVARIANT_PIN
    return CLAIM_KIND_IMPROVEMENT


def is_invariant_pin(row: dict[str, Any]) -> bool:
    """True for tautological pins that are not improvement claims.

    Pins pass by construction and must not pad the recency window to TRUST.
    Both explicit ``claim_kind="invariant_pin"`` rows and legacy trust-pin
    receipt names are excluded before any windowing happens.
    """
    return claim_kind(row) == CLAIM_KIND_INVARIANT_PIN


def is_goodhart_excluded_row(row: dict[str, Any]) -> bool:
    return is_invariant_pin(row) or is_goodhart_excluded_receipt_id(receipt_id(row))


def load_rows(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def filter_rows(
    rows: list[dict[str, Any]],
    *,
    require_measured: bool = False,
    window: int | None = None,
    change_class: str | None = None,
    exclude_pins: bool = True,
) -> list[dict[str, Any]]:
    # Exclude tautological invariant pins BEFORE windowing, so the recency window
    # reflects genuine improvement claims and cannot be padded to TRUST.
    base = [r for r in rows if not (exclude_pins and is_goodhart_excluded_row(r))]
    scoped = base[-window:] if window and window > 0 else list(base)
    if require_measured:
        scoped = [r for r in scoped if r.get("scored_by") == SCORED_BY_MEASURED]
    if change_class:
        scoped = [r for r in scoped if str(r.get("change_class") or "unclassified") == change_class]
    return scoped


def high_confidence_hit_rate(
    rows: list[dict[str, Any]],
    *,
    threshold: float = HIGH_CONFIDENCE_THRESHOLD,
) -> tuple[float, int]:
    high = [r for r in rows if float(r.get("confidence", 0)) >= threshold]
    if not high:
        return 0.0, 0
    rate = sum(1 for r in high if r.get("held")) / len(high)
    return rate, len(high)


def trust_verdict(
    rows: list[dict[str, Any]],
    *,
    min_hit_rate: float = DEFAULT_MIN_HIT_RATE,
    require_measured: bool = False,
    window: int | None = None,
    change_class: str | None = None,
    exclude_pins: bool = True,
    high_confidence_threshold: float = HIGH_CONFIDENCE_THRESHOLD,
) -> dict[str, Any]:
    filtered = filter_rows(
        rows,
        require_measured=require_measured,
        window=window,
        change_class=change_class,
        exclude_pins=exclude_pins,
    )
    rate, high_n = high_confidence_hit_rate(filtered, threshold=high_confidence_threshold)
    out: dict[str, Any] = {
        "claims": len(filtered),
        "high_confidence_claims": high_n,
        "high_confidence_hit_rate": round(rate, 4),
        "min_hit_rate": min_hit_rate,
        "require_measured": require_measured,
        "window": window,
        "change_class": change_class,
    }
    if not filtered:
        out["verdict"] = "GATE"
        out["reason"] = "no claims in scope"
        return out
    out["verdict"] = "TRUST" if rate >= min_hit_rate else "GATE"
    return out


def class_status(
    rows: list[dict[str, Any]],
    *,
    min_hit_rate: float = DEFAULT_MIN_HIT_RATE,
    require_measured: bool = True,
    window: int | None = None,
    exclude_pins: bool = True,
    high_confidence_threshold: float = HIGH_CONFIDENCE_THRESHOLD,
    min_track_record: int = MIN_TRACK_RECORD,
) -> dict[str, dict[str, Any]]:
    """Graduated-autonomy status per change class.

    ``window`` is applied PER CLASS (each class is judged on its own last-N
    claims), not across the whole ledger: with a shared global window, scoring
    a burst of claims in one class evicts other classes' recent track records.
    A class's standing must only move on evidence about that class.
    """
    scoped = filter_rows(rows, require_measured=require_measured, exclude_pins=exclude_pins)
    class_rows: dict[str, list[dict[str, Any]]] = {}
    for row in scoped:
        class_rows.setdefault(str(row.get("change_class") or "unclassified"), []).append(row)
    out: dict[str, dict[str, Any]] = {}
    for name, crows in sorted(class_rows.items()):
        recent = crows[-window:] if window and window > 0 else crows
        holds = [
            bool(row.get("held"))
            for row in recent
            if float(row.get("confidence", 0)) >= high_confidence_threshold
        ]
        count = len(holds)
        rate = sum(holds) / count if count else 0.0
        if rate >= min_hit_rate and count >= min_track_record:
            status = "auto-merge ELIGIBLE"
        elif count < min_track_record:
            status = f"GATE (track record {count}/{min_track_record})"
        else:
            status = f"GATE (hit-rate < {min_hit_rate:.0%})"
        out[name] = {"hit_rate": round(rate, 4), "n": count, "status": status}
    return out
