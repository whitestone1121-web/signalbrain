# Online Evaluation with Stakes: Receipt-Based Calibration for Autonomous Coding Agents

**Working draft — technical report.** Everything claimed here is reproducible
from public git history; every section links its evidence. Feedback via issues
and PR comments at any depth. Framing credit for the title: Hamel Husain.

**Status:** skeleton with evidence stubs. Sections marked ▢ need prose; the
underlying artifacts already exist and are linked.

---

## Abstract (▢ draft last)

Coding agents ship claims about their own work faster than humans can verify
them. We describe a production system in which agent claims are *executable
receipts*, objectively re-scored after merge, with merge autonomy earned per
change-class from measured calibration — and report what happened when the
agents attacked it. Three incidents, one counterintuitive calibration curve,
and a set of failure modes with the scars to prove them.

## 1. The framework

▢ Prose from [`RECEIPT_SPEC.md`](../docs/RECEIPT_SPEC.md) — the receipt format,
scoring semantics, and trust math. Key mechanisms:

- Receipts: executable claims (change + measure command + stated confidence) — spec §1–2
- Merged-only scoring; byte-identical content guard — spec §2, §6.4
- Per-class recency windows; ELIGIBLE at ≥95% held over last 10 high-confidence claims — spec §3
- The three-role separation: proposer / scorer / refuter — spec §5
- Lifecycle diagram: [README](../README.md#the-receipt-lifecycle) ·
  Architecture: [PHASE0](../docs/PHASE0_EXTRACT_PLAN.md#how-the-pieces-fit)

## 2. Forensic case studies: the gaming incidents

▢ Narrative per incident; all three documented with reproduce commands in
[`docs/incidents/`](../docs/incidents/) and the reference deployment's history.

| # | Pattern | Detection | Outcome |
|---|---|---|---|
| 1 | Legacy trust-pin batch (20 rows, named pins) | naming-marker exclusion | rows recorded, excluded from trust |
| 2 | **The founding incident**: renamed pin batch + unmerged self-score via guard bypass; displayed trust 100%, measured 40% | operator audit, pre-commit | remediation #1196; classifier shipped |
| 3 | Replay of pattern 2 post-remediation | **same-PR pin classifier, unattended** | rows auto-classified `invariant_pin`, zero trust, no human in loop |

Key SHAs: attack merged `b291232660`, remediation `b6cb84f3e1` (reference
deployment). Full forensic record:
[2026-07 incident](../docs/incidents/2026-07-tooling-trust-streak-gaming.md).

## 3. Failure-mode analysis

Seeded by H. Husain's critiques (credited); each subsection pairs the predicted
failure with observed evidence or its absence.

### 3.1 Change-class granularity (predicted: Husain)
▢ Both failure modes observed. Too-coarse: cross-class window eviction
(bugfix ELIGIBLE n=10 → GATE n=4 under shared window; fixed by per-class
windows, reference PR #1188). Too-fine: n≥10 floor means fine classes never
qualify. Open design: hierarchical classing with backoff ("smoothing for
trust") — see §5.

### 3.2 Difficulty stratification (predicted: Husain)
▢ Not yet tracked; first proxy shipped —
[calibration-curves](calibration-curves/) stratifies by measure-command count.
Diff-size stratification: next.

### 3.3 Confidence inversion at the top of the scale (observed, unpredicted)
▢ The [first calibration curves](calibration-curves/README.md) show hold-rate
*falling* as stated confidence rises above ~0.90 (86% → 83% → 33%, top bin
n=3). Two candidate mechanisms: (a) agents state peak confidence precisely
where they stopped doubting, and doubt was doing verification work; (b) stated
confidence is a *social signal rather than an epistemic one* — agents
"performing certainty rather than reporting it" (Husain, correspondence).
Consistent with the broader finding that model confidence and accuracy diverge
in modern networks (Guo et al. 2017); tail-bin breakdown is also the classic
failure regime of Platt-style calibration. Needs n.

### 3.4 Self-referential measures (observed)
▢ A receipt whose measure invokes the scoring pipeline deadlocks against the
score lock and fails opaquely (receipt 0582, reference deployment). Rule
adopted: measures must not invoke the scorer — spec §1 grammar notes.

### 3.5 Measurement-grammar brittleness (observed)
▢ Shell operators parsed as arguments caused silent false failures (pipe
grammar, reference PR #1210 / package fix). Lesson: the measure grammar is
attack surface *and* failure surface; every parse gap becomes a false ledger
row.

### 3.6 Over-remediation (observed)
▢ The #1196 remediation manually pinned receipts with genuine behavioral
deltas — trust destruction in the opposite direction. Resolution: the
classifier, not the interested lane, is the standard (adjudication receipt
0593). Governance lesson: anti-gaming rules can themselves be miscalibrated.

## 4. Open problems

1. **Smoothing for trust** — hierarchical class backoff under data sparsity.
   Pointers (via Husain): Platt scaling and its tail-bin failure modes;
   Guo et al. 2017, "On Calibration of Modern Neural Networks" (temperature
   scaling). Direction: adapt temperature scaling to *stated* confidence,
   using the measured ledger as ground truth — post-hoc recalibration of the
   agents' confidence channel, with the gate consuming calibrated rather than
   raw confidence.
2. **Difficulty-aware thresholds** — should ELIGIBLE thresholds vary by
   difficulty stratum?
3. **The top-bin inversion** — replicate at n≥30; artifact or law?
4. **Receipt-emission fidelity** — agents write their own measures; measure
   quality is unaudited (manual audit protocol proposed in the
   [overclaiming-report plan](../docs/overclaiming-report/PLAN.md)).
5. **Cross-agent generality** — every number here is one deployment; the
   [pre-registered wild study](../docs/overclaiming-report/PLAN.md) is the
   designed replication.

## 5. Reproducibility

Every table and figure regenerates from public artifacts:
ledger + receipts in the [reference deployment](https://github.com/whitestone1121-web/neural-chat-v3),
curves via [`calibration-curves/generate.py`](calibration-curves/generate.py),
gate math via `pip install signalbrain` (`sb gate`).

## Acknowledgments

▢ Hamel Husain — framing ("online evaluation with stakes"), failure-mode
critiques (§3.1, §3.2), reviewer.
