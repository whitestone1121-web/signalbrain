# The Agent Overclaiming Report — methodology (pre-registered)

Goal: the first measured, reproducible overclaim rate for a popular coding agent
in the wild. Whatever number we measure, we publish — including a boring one.
This plan is committed BEFORE any runs so the methodology can't drift toward a
desired result (the same rule the ledger enforces on our own agents).

## Question

When a coding agent states high confidence (≥0.85) that its change achieves the
claimed effect, how often does the claim hold under objective re-scoring?

## Method

1. **Agent**: one widely-used coding agent (operator decision — candidate:
   Claude Code headless). Version pinned in the report.
2. **Tasks**: 50 tasks sampled from public repos — a fixed, published list.
   Sources: SWE-bench-lite subset (30) + 20 real open issues labeled
   `good-first-issue`/`bug` from active OSS repos. Sampling script + seed committed.
3. **Receipt emission**: the agent receives the task plus the receipt-emission
   prompt template (`docs/pilot/receipt-emission.md`): it must state what changed,
   an executable `### How measured` command, and its confidence.
4. **Merge simulation**: the change is committed to the task repo's scratch clone
   (merged-ref = HEAD), satisfying the guard exactly as a human merge would.
5. **Scoring**: `sb score` re-runs each receipt's own measure. Same-PR-test-only
   pins are classified and reported separately (they are their own finding:
   "N% of agent receipts were self-referential").
6. **Report**: hit-rate by confidence band, by task type, and by pin
   classification; ledger + all receipts + task list published in full.

## Threats to validity (stated up front)

- The agent writes its own measures — weak measures inflate hold-rate. We report
  measure quality (does the command exercise the claimed behavior?) via manual
  audit of a 10-task sample, disclosed as a limitation.
- Task sample is not representative of enterprise codebases. Stated in the report.
- One agent ≠ all agents. The report invites replication; the harness is public.

## Cost & decision needed from the operator

~50 agent runs ≈ operator API budget approval + agent choice. No runs start
until both are given. Estimated wall-clock: 2–3 supervised evenings.

## Deliverables

- `report/` — the writeup with every number linked to a ledger row
- `harness/` — task sampler, runner, scoring pipeline (reproducible end-to-end)
- One-line finding for outreach: "measured overclaim rate: X% at ≥0.85 stated confidence"
