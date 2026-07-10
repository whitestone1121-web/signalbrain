# We pointed a trust ledger at 560 real PRs from 8 autonomous coding agents

*Draft — not published. Every number below is re-derivable from GitHub's public API.*

Autonomous coding agents ship code now — Devin, Cursor, Codegen, Google's Jules,
Factory's Droid, Ellipsis, Sourcery, and Tembo open PRs on public repos every day.
They also tell you the work is done: *"all tests pass," "verified," "no regressions."*

So we asked the only question a trust layer asks: **does the agent's stated claim
match the repo's recorded evidence?** We took the 70 most-recent closed PRs from
each of 8 agents (560 total), and for each one compared what the PR *said* against
what GitHub actually *records* — CI conclusions, merge state, reverts. No test
suites were re-run; the ground truth is the repo's own recorded outcome, which is
public and stronger than self-report.

## What we found

| | count | of |
|---|---|---|
| PRs audited | **560** | 8 agents × 70 |
| merged | 346 | — |
| **merged with NO recorded verification evidence** | **162 (47%)** | of merges |
| stated an explicit verification claim or test plan | 129 | — |
| **claim contradicted by recorded evidence (hard catch)** | **4** | across 3 agents |
| claimed success but PR closed un-merged | 33 | weaker signal |
| claim + a failing CI job (needs per-check review) | 8 | see below |

The headline isn't that agents lie. It's that **most agent merges leave nothing to
verify.** 47% of merged PRs (162 of 346) had no CI, no checked-off test plan, no
re-runnable claim — the change simply landed. You cannot audit what was never
recorded — and the number got *worse* as we widened the sample, not better.

## The clean catches (3 incidents, 3 different agents)

Each is a case where the agent's own artifacts contradict the "done" story. Links
are live; check them yourself.

1. **Devin — merged a fix, then reverted its own regressions (twice).**
   [`H-Gripe-Studio#647`](https://github.com/tanzanite2025/H-Gripe-Studio/pull/647)
   ("Fix invisible native window startup") merged. Then
   [`#648`](https://github.com/tanzanite2025/H-Gripe-Studio/pull/648) —
   *"Revert two regressions from #647"* — by the same agent. Same pattern in a second
   repo: [`skin-changer#5`](https://github.com/5thDimension-Sean/skin-changer/pull/5)
   merged, [`#10`](https://github.com/5thDimension-Sean/skin-changer/pull/10) reverts it.

2. **Codegen — merged a new engine, then urgently reverted it.**
   [`score-phantom#1`](https://github.com/Heisdawrld/score-phantom/pull/1)
   ("🚀 Switch to New Prediction Engine…") merged. Immediately followed by
   [`#2`](https://github.com/Heisdawrld/score-phantom/pull/2) —
   *"🔄 URGENT: Revert to Old Prediction Engine."*

3. **Cursor — merged with a 6-step test plan, zero steps done.**
   [`MidTN#24`](https://github.com/jsteiml/MidTN/pull/24) shipped a "## Test plan"
   with six checkboxes — *open the list, confirm the column, create a customer,
   export CSV, deploy and verify `/api/health`* — **all six unchecked, and zero CI
   ran.** The plan was written; there is no record any of it was executed.

## How this audit polices itself

An audit that catches overclaims has to hold itself to the same bar — or it *is* the
thing it's criticizing. So we re-verified every candidate, and **dropped every one
that didn't survive:**

- [`agrr#174`](https://github.com/rick-chick/agrr/pull/174) *looked* like a catch —
  it claimed "2969 tests passed" and the aggregate CI showed a failure. But the
  failing job was `dispatch` (a deploy step); the `frontend-test` job the claim
  actually refers to **passed.** The claim was true. **Dropped** — and the whole
  CI-vs-claim signal was demoted to "needs manual review," never counted in the headline.
- [`reqsys#674`](https://github.com/ericson-j-santos/reqsys-v2-enterprise-real/pull/674)
  tripped a "revert" flag — but it's a docs PR; the word only appears as advice
  (*"revert the commit if any inaccuracy is found"*). **Dropped**, and we tightened the
  rule to require an explicit `#PR` reference before anything counts as a revert.

That discipline — re-checking a plausible claim against the *specific* evidence
instead of an aggregate or a keyword — is exactly what agents skip, and exactly what a
trust layer automates. The 4 catches that remain are the ones that survived it.

## Why this matters — and what to do about it

Agents are getting better at *writing* code and *claiming* it works. The missing
layer is the one that **re-scores the claim against re-runnable evidence** and lets
autonomy be *earned by track record* instead of asserted per-PR. An overclaim should
count against an agent's trust — permanently — and a self-measured "test I wrote
myself" should earn zero. That asymmetry is the product.

- **See it on 3 receipts in 2 minutes:** <https://github.com/whitestone1121-web/receipt-gate-demo>
  — fork it, watch a trust ledger catch an agent's overclaim, re-derive the verdict yourself.
- **Add it to your own agent:** `pip install govern-kit` — receipts with re-runnable
  evidence, a measured-only calibration ledger, per-class autonomy gates, signed rows,
  a kill switch. <https://pypi.org/project/govern-kit/>

## Reproduce this audit

The harness is ~200 lines of Python over the GitHub API — no scraping, no private
data. `python agent_trust_audit.py "app/devin-ai-integration,app/cursor,…" 70`.
Every verdict in the ledger carries the PR URL, the claim quote, and the contradicting
signal. Run it against any agent author and any window; the numbers move, the method
doesn't.

*Method notes: "recorded evidence" = GitHub check-runs / combined status on the head
SHA + merge state + revert references. A "hard catch" requires an unambiguous
contradiction (a revert of the agent's own merged work, or a merge whose stated
verification has zero recorded execution). Circumstantial signals (claim + un-merged
close; claim + an unrelated failing job) are reported separately and never counted in
the headline.*
