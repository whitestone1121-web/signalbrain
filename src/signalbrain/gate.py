"""Trust gates — global and per-class (SPEC §3).

Config-first port of neural-chat-v3 `calibration_autonomy_gate`. Env variables
use the SIGNALBRAIN_ prefix and are fallbacks; explicit arguments always win.
There is deliberately no bypass env: the only override anywhere is the scorer's
loud ``allow_unmerged``.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .ledger import (
    DEFAULT_MIN_HIT_RATE,
    DEFAULT_RECENCY_WINDOW,
    class_status,
    load_rows,
    trust_verdict,
)

WINDOW_ENV = "SIGNALBRAIN_WINDOW"
MIN_HIT_RATE_ENV = "SIGNALBRAIN_MIN_HIT_RATE"
RECENCY_GATE_ENV = "SIGNALBRAIN_RECENCY_GATE"
DUAL_GATE_ENV = "SIGNALBRAIN_DUAL_GATE"


def _truthy(env: dict[str, str], key: str) -> bool:
    return str(env.get(key, "")).strip().lower() in ("1", "true", "yes", "on")


def window_from_env(env: dict[str, str] | None = None) -> int | None:
    env = env if env is not None else dict(os.environ)
    raw = str(env.get(WINDOW_ENV, "")).strip()
    if not raw:
        return None
    try:
        value = int(raw)
    except ValueError:
        return None
    return value if value > 0 else None


def min_hit_rate_from_env(env: dict[str, str] | None = None) -> float:
    env = env if env is not None else dict(os.environ)
    raw = str(env.get(MIN_HIT_RATE_ENV, "") or DEFAULT_MIN_HIT_RATE).strip()
    try:
        value = float(raw)
    except ValueError:
        return DEFAULT_MIN_HIT_RATE
    return value if 0.0 < value <= 1.0 else DEFAULT_MIN_HIT_RATE


def recency_only_from_env(env: dict[str, str] | None = None) -> bool:
    """Operator opt-in: gate on the recency window only (past failures fade)."""
    env = env if env is not None else dict(os.environ)
    if _truthy(env, DUAL_GATE_ENV):
        return False
    return _truthy(env, RECENCY_GATE_ENV)


def per_class(ledger_path: Path, *, window: int | None = None, env: dict[str, str] | None = None) -> dict[str, dict[str, Any]]:
    """Per-class auto-merge status. The window resolves: arg > env > default.

    One source of truth for BOTH the report and any merge decision — a rail
    that reads a different window than the operator's report is a fake-green.
    """
    w = window if window is not None else (window_from_env(env) or DEFAULT_RECENCY_WINDOW)
    return class_status(load_rows(ledger_path), window=w, require_measured=True)


def eligible_classes(ledger_path: Path, *, window: int | None = None, env: dict[str, str] | None = None) -> list[str]:
    status = per_class(ledger_path, window=window, env=env)
    return sorted(name for name, row in status.items() if row.get("status") == "auto-merge ELIGIBLE")


def widening_allowed(
    ledger_path: Path,
    *,
    env: dict[str, str] | None = None,
) -> tuple[bool, dict[str, Any]]:
    """Global trust gate. Dual by default (full history AND recency window ≥ min rate);
    SIGNALBRAIN_RECENCY_GATE=1 opts into recency-only."""
    env = dict(env if env is not None else os.environ)
    min_rate = min_hit_rate_from_env(env)
    rows = load_rows(ledger_path)
    full = trust_verdict(rows, min_hit_rate=min_rate, require_measured=True, window=None)
    recency_window = window_from_env(env) or DEFAULT_RECENCY_WINDOW
    recency = trust_verdict(rows, min_hit_rate=min_rate, require_measured=True, window=recency_window)
    if recency_only_from_env(env):
        allowed = recency.get("verdict") == "TRUST"
        reason = "recency-windowed measured gate (full history advisory; operator opt-in)"
    else:
        allowed = full.get("verdict") == "TRUST" and recency.get("verdict") == "TRUST"
        reason = "dual gate: full measured history and recency window must both TRUST"
    return allowed, {
        "verdict": "TRUST" if allowed else "GATE",
        "reason": reason,
        "operative_gate": "recency_window" if recency_only_from_env(env) else "dual",
        "full_history": full,
        "recency_window": recency,
        "recency_window_size": recency_window,
    }
