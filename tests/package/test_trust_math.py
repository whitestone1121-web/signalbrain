"""Packaged trust-math contracts: per-class windowing, pin exclusion, in-place rescore."""

from __future__ import annotations

import json

from signalbrain.ledger import class_status, filter_rows, high_confidence_hit_rate, trust_verdict
from signalbrain.scorer import append_row, existing_receipt_ids, replace_receipt_rows


def _row(rid, held, change_class="tooling", confidence=0.9, **kw):
    return {
        "claim": rid,
        "confidence": confidence,
        "held": held,
        "scored_by": "measured",
        "change_class": change_class,
        "receipt_id": rid,
        **kw,
    }


def test_burst_in_one_class_does_not_evict_another():
    rows = [_row(f"bugfix-{i}", True, "bugfix") for i in range(10)]
    baseline = class_status(rows, window=20)["bugfix"]
    assert baseline["status"] == "auto-merge ELIGIBLE"
    rows += [_row(f"tooling-{i}", i % 2 == 0, "tooling") for i in range(25)]
    assert class_status(rows, window=20)["bugfix"] == baseline


def test_window_applies_within_class():
    rows = [_row(f"old-{i}", False) for i in range(5)]
    rows += [_row(f"win-{i}", True) for i in range(20)]
    status = class_status(rows, window=20)["tooling"]
    assert status == {"hit_rate": 1.0, "n": 20, "status": "auto-merge ELIGIBLE"}


def test_failures_do_not_age_out_via_other_classes():
    rows = [_row("fail", False)] + [_row(f"win-{i}", True) for i in range(10)]
    rows += [_row(f"bugfix-{i}", True, "bugfix") for i in range(30)]
    status = class_status(rows, window=20)["tooling"]
    assert status["n"] == 11
    assert "GATE" in status["status"]


def test_pins_cannot_pad_any_window():
    rows = [_row(f"win-{i}", True) for i in range(5)]
    rows += [_row(f"pin-{i}", True, claim_kind="invariant_pin") for i in range(10)]
    rows += [_row(f"legacy-trust-pin-{i}", True) for i in range(5)]  # name-marker exclusion
    status = class_status(rows, window=20)["tooling"]
    assert status["n"] == 5
    assert "GATE" in status["status"]
    rate, n = high_confidence_hit_rate(filter_rows(rows, require_measured=True, window=10))
    assert n == 5  # pins excluded BEFORE windowing


def test_track_record_minimum():
    rows = [_row(f"win-{i}", True) for i in range(9)]
    assert "track record 9/10" in class_status(rows, window=20)["tooling"]["status"]


def test_trust_verdict_thresholds():
    rows = [_row(f"win-{i}", True) for i in range(19)] + [_row("fail", False)]
    v = trust_verdict(rows, require_measured=True, window=20)
    assert v["verdict"] == "TRUST"  # 19/20 = 95%
    rows.append(_row("fail-2", False))
    v = trust_verdict(rows, require_measured=True, window=20)
    assert v["verdict"] == "GATE"  # 18/20 = 90%


def test_low_confidence_rows_do_not_count():
    rows = [_row(f"low-{i}", False, confidence=0.5) for i in range(10)]
    rows += [_row(f"win-{i}", True) for i in range(10)]
    status = class_status(rows, window=20)["tooling"]
    assert status["n"] == 10
    assert status["hit_rate"] == 1.0


def test_replace_preserves_position_and_drops_dupes(tmp_path):
    ledger = tmp_path / "ledger.jsonl"
    ledger.write_text("".join(json.dumps(r) + "\n" for r in [_row("old", False), _row("b1", True), _row("old", False), _row("b2", True)]))
    matched = replace_receipt_rows(ledger, "old", _row("old", True))
    assert matched == 2
    ids = [json.loads(ln)["receipt_id"] for ln in ledger.read_text().splitlines() if ln.strip()]
    assert ids == ["old", "b1", "b2"]
    assert json.loads(ledger.read_text().splitlines()[0])["held"] is True


def test_append_dedups_by_receipt_id(tmp_path):
    ledger = tmp_path / "ledger.jsonl"
    ledger.write_text(json.dumps(_row("a", True)) + "\n")
    assert append_row(ledger, _row("a", False)) is False
    assert append_row(ledger, _row("b", True)) is True
    assert existing_receipt_ids(ledger) == {"a", "b"}
