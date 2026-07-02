# 0593 — tooling: pin adjudication by classifier standard + 0580 mode-artifact rescore

## Compared
- branch:    `fix/calibration-pin-adjudication-0593@HEAD`
- baseline:  `origin/main@34ac430916`
- date:      `2026-07-02`

## Change summary

Two ledger corrections, both mechanical and operator-reviewable:

1. **Pin adjudication.** #1196 manually marked 7 rows `invariant_pin`. Re-judged
   every one with the shipped classifier (`calibration_same_pr_pin.
   is_same_pr_test_only_pin`, the repo's own definition of a pin): **0575-footer
   and 0576-runbook stay pinned** (measured solely by tests their own merge
   introduced); **0577 / 0578 / 0579 / 0581 / 0583 are unpinned** (non-pytest
   measures or pre-existing test targets — behavioral changes verified partly by
   tests that could have failed). Adjudicated by the code's standard, not by any
   interested lane; the one-command reproduction is below. Disclosure: 0579/0581
   were authored by the lane submitting this PR — which is why the classifier,
   not the author, is the judge.
2. **0580 rescore.** `0580-…-merged-score-guard` read `held=false` because the
   guard script's executable bit was stripped in a working tree (git has 100755;
   the contract asserts executability). Mode restored; measure re-run green;
   row rewritten **in place** via `CALIBRATION_RESCORE=1` (the 0581 machinery).

Also clarifies RECEIPT_SPEC §6.2: manual pinning must match the classifier
standard or document its divergence, and flags the measure-grammar pipe
limitation that 0582's failure exposed.

## Metric delta

| Metric | Baseline | Branch | Delta |
|---|---|---|---|
| Rows pinned | 7 | 2 | -5 (classifier-standard) |
| 0580 held | false (env artifact) | true (measure green) | honest rescore |
| bugfix class (w=10) | ELIGIBLE 100% n=10 | ELIGIBLE 100% n=10 | unchanged |
| tooling class (w=10) | GATE 40% n=10 | GATE 50% n=10 | +10pt, still GATE |
| recency-10 TRUST | GATE 40% | GATE 50% | still GATE |

No gate flips: this correction is trust-neutral at the gate level — it restores
classification principle (genuine measured wins may earn trust; tautological
pins may not) without opening anything.

### How measured

```bash
python3 -m pytest tests/contracts/test_calibration_merged_score_guard_contract.py -q
python3 -c "import json; rows=[json.loads(l) for l in open('docs/calibration/improvement_claim_ledger.jsonl') if l.strip()]; rid=lambda r: str(r.get('receipt_id') or r.get('claim') or ''); pins={rid(r) for r in rows if r.get('claim_kind')=='invariant_pin'}; assert '0575-tooling-automerge-receipt-class-footer' in pins and '0576-tooling-operator-receipt-class-runbook' in pins, pins; assert not pins & {'0577-tooling-supervised-lane-measure-hygiene','0578-tooling-calibration-scorer-inline-env','0579-tooling-calibration-per-class-window','0581-tooling-calibration-rescore-preserves-order','0583-tooling-scorer-receipt-class-footer'}, pins; r580=[r for r in rows if rid(r)=='0580-tooling-calibration-merged-score-guard']; assert r580 and r580[0]['held'] is True"
```

## Verdict

`improvement`

## Confidence

0.9

## Reasoning

The classifier is the repo's committed definition of a pin; manual batches that
diverge from it in either direction (padding OR over-pinning) make the ledger
mean something different from what the code says it means. Reproduce the
adjudication: for each pinned receipt, parse its measure commands and run
`is_same_pr_test_only_pin(root, rel, commands, merged_ref='origin/main')`.

## change_class

tooling
