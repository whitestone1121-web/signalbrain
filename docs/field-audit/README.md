# Do AI coding agents leave anything you can verify? An audit of 560 real pull requests

**A field study of eight autonomous coding agents, with a fully reproducible method
and a scored, published ledger. Every number below can be re-derived from GitHub's
public API. Every claim about a specific pull request links to that pull request.**

---

## Abstract

Autonomous coding agents now open and merge pull requests on public repositories at
scale, and they routinely assert that the work is done and correct — "all tests pass,"
"verified," "no regressions." We asked a single, narrow question of 560 of those pull
requests, 70 from each of eight agents: **does the agent's stated claim match the
evidence the repository actually recorded?** We did not re-run any test suites; the
ground truth is GitHub's own record — CI conclusions, merge state, and revert history —
which is public and stronger than self-report.

Two findings. First, and most important: **47% of merged agent pull requests left no
recorded verification evidence at all** — no CI, no completed test plan, no re-runnable
claim. There is simply nothing to audit. Second, in a smaller number of cases the
agent's own artifacts contradicted its "done" story: an agent merging a change and then
urgently reverting it, or merging a written test plan with zero of its steps executed.
We report four such "hard catches," each of which survived a deliberate second round of
adversarial re-verification — a round in which we **dropped several of our own initial
findings** because they did not hold up. That self-check is the whole point: it is the
discipline the agents skipped, and it is exactly what a trust layer automates.

---

## TL;DR (the numbers)

- **560** pull requests audited — the 70 most-recent *closed* PRs from each of 8 agents.
- **346** were merged.
- **162 of 346 (47%)** merged PRs had **no recorded verification evidence**.
- **129** PRs stated an explicit verification claim or test plan.
- **4** hard catches (claim contradicted by the agent's own recorded artifacts), across **3** of the 8 agents.
- **5 of 8** agents had **zero** hard catches.
- Several candidate catches were **dropped** after re-verification (documented below).

Every row of the scored ledger, with the verdict and a link, is published:
`agent_trust_ledger.jsonl` (560 rows). The scoring program is ~200 lines of Python:
`agent_trust_audit.py`.

---

## 1. Why we ran this

The industry is shipping autonomy faster than it is shipping the ability to *check*
autonomy. An agent that writes a plausible diff and a confident PR description is easy
to build; a system that establishes whether the diff actually did what the description
claims is not. Our thesis — the reason SignalBrain exists — is that the missing layer in
agentic software is a **trust layer**: something that re-scores an agent's claim against
re-runnable evidence and lets autonomy be *earned by track record* rather than asserted
per pull request.

Before asking anyone to believe that thesis, we wanted to measure whether the problem it
addresses is real and observable in the wild. So we pointed the exact question a trust
layer asks — *claim vs. recorded evidence* — at a public, reproducible sample of real
agent output.

---

## 2. Method

The method is deliberately simple, conservative, and reproducible. There is no scraping,
no private data, and no human judgement in the scoring loop beyond the rules stated here.

### 2.1 Data source and sampling

We used the GitHub search and REST APIs. For each agent we queried the **70 most-recent
closed pull requests authored by that agent's bot account**:

```
app/devin-ai-integration   app/cursor        app/google-labs-jules   app/codegen-sh
app/factory-droid          app/ellipsis-dev  app/sourcery-ai         app/tembo
```

"Closed" (merged or closed-unmerged) is deliberate: only a resolved PR has a final,
checkable outcome. Deduplicated, this yields 560 distinct pull requests. The sample is
"most-recent" at run time — re-running later shifts the window, which is a feature: the
method is stable even though the exact PRs move.

### 2.2 The question, and the scoring rubric

For each PR we compared its **stated claim** (from the PR body) against the **recorded
evidence** (from GitHub): the aggregate CI conclusion on the head commit, the merge
state, and whether the PR is a revert of a prior PR. Each PR receives exactly one verdict:

| Verdict | Definition |
|---|---|
| **held** | Merged, and the claim is backed — CI green on the head commit, or a completed (ticked) verification checklist. |
| **CAUGHT** | An unambiguous contradiction between claim and recorded evidence. Only two patterns qualify (see §2.3). |
| **claim-vs-ci-review** | An explicit success claim *and* at least one failing CI job — but the failing job may be unrelated to the claim, so this is flagged for manual review, **never counted as a catch**. |
| **rejected-with-claim** | An explicit success claim, but the PR was closed **without** merging. Circumstantial (PRs close for many reasons); reported separately, never a headline number. |
| **unverifiable** | No explicit claim and nothing to re-check — including the important sub-case *merged with no recorded evidence at all*. |

### 2.3 What counts as a "hard catch" (the conservative core)

A **CAUGHT** verdict requires one of exactly two unambiguous conditions:

1. **A revert of the agent's own prior merged work**, where the reverting PR names the
   specific prior PR (`revert … #N`). We require the explicit `#N` reference precisely so
   that a keyword match on the word "revert" cannot produce a false positive (see §4).
2. **A merge whose stated verification was never executed** — a PR that (a) is merged,
   (b) contains a checklist under a *test / verification / QA* heading with **two or more
   boxes and none checked**, and (c) has **no green CI** on the head commit. This is not a
   claim that the code is broken; it is the stricter, verifiable claim that **the stated
   verification has zero recorded evidence of having run.**

Everything softer than this — an unrelated failing CI job, a claim on a PR that closed
for unknown reasons — is reported in its own bucket and excluded from the headline.

### 2.4 Fail-closed, and what we did *not* do

- We did **not** execute any project's test suite. Re-running arbitrary external suites
  requires each repo's environment and introduces its own errors; instead we rely on the
  outcome the repository itself recorded, which is public and immutable.
- "Unknown" never scores as "safe." A PR with no claim and no evidence is `unverifiable`,
  not `held`.
- The scoring is pure and deterministic given the API responses. The full program is
  published; the interesting predicates (`allowlist`-style checks, revert parsing,
  checkbox counting) are plain functions you can read and test.

---

## 3. Results

### 3.1 Aggregate (560 PRs)

| Outcome | Count |
|---|---:|
| Merged with re-checkable evidence (**held**) | 177 |
| **Merged with no recorded verification evidence** | **162** |
| Claim contradicted by recorded evidence (**hard catch**) | 4 |
| Claimed success, but closed un-merged | 33 |
| Claim + a failing CI job (needs manual review) | 8 |
| Closed, no claim — nothing to re-check | 176 |
| **Total** | **560** |

Of **346 merged** PRs, **162 (47%)** had no recorded verification evidence.

### 3.2 Per-agent distribution (the honest picture)

The aggregate hides wide variation, and reporting only the aggregate would be its own
kind of overclaim. Here is every agent:

| Agent | PRs | held | merged / no-evidence | hard catches |
|---|---:|---:|---:|---:|
| google-labs-jules | 70 | 52 | 17 / 69 (25%) | 0 |
| cursor | 70 | 36 | 1 / 39 (3%) | 1 |
| factory-droid | 70 | 27 | 8 / 35 (23%) | 0 |
| codegen-sh | 70 | 19 | 14 / 35 (40%) | 1 |
| devin-ai-integration | 70 | 16 | 46 / 65 (71%) | 2 |
| tembo | 70 | 15 | 14 / 29 (48%) | 0 |
| ellipsis-dev | 70 | 10 | 21 / 31 (68%) | 0 |
| sourcery-ai | 70 | 2 | 41 / 43 (95%) | 0 |

**What this does and does not say.** Cursor and Jules mostly *do* leave evidence — Cursor
had a single-digit no-evidence rate. The high no-evidence rates (Sourcery 95%, Devin 71%)
are dominated by the kind of PRs those agents open and the repos they open them in:
Sourcery's automated micro-refactors and many Devin/Ellipsis changes land in small public
repositories that run no CI at all. **"No recorded evidence" is a statement about the
public record, not a verdict on an agent's competence** — the code may well have been
tested locally. But that is precisely the auditability gap: if nothing was recorded, no
reviewer, teammate, or downstream system can ever check the claim. Only **three** of eight
agents produced a hard catch; **five produced none.** This is not "agents are reckless."
It is "the substrate that would let you *know* is usually absent."

---

## 4. The hard catches (verify each yourself)

Each of the four is a case where the agent's *own* recorded artifacts contradict the
"done" story. Links are live and immutable.

### 4.1 Codegen — merged a new engine, then urgently reverted it
Repo `Heisdawrld/score-phantom`.
- **#1** *"🚀 Switch to New Prediction Engine with Anti-Repetition & Improved Scoring"* — **merged.**
- **#2** *"🔄 URGENT: Revert to Old Prediction Engine"* — **merged**, reverting #1.
- Verify: <https://github.com/Heisdawrld/score-phantom/pull/2>

### 4.2 Devin — reverted its own merged work, in two different repositories
- `tanzanite2025/H-Gripe-Studio` **#647** *"Fix invisible native window startup"* merged;
  **#648** summary: *"Revert two regressions from #647 …"*.
  Verify: <https://github.com/tanzanite2025/H-Gripe-Studio/pull/648>
- `5thDimension-Sean/skin-changer` **#10** *"Reverts to the known-stable PR #5 state. PRs
  6-9 introduced various model-swap attempts that **all crashed the game**. This removes
  ALL of them."* Four successive merges regressed before a mass rollback.
  Verify: <https://github.com/5thDimension-Sean/skin-changer/pull/10>

### 4.3 Cursor — merged a test plan it never executed
Repo `jsteiml/MidTN` **#24** — merged, with **zero CI checks** recorded on the head
commit, carrying this checklist verbatim:

```
## Test plan
- [ ] Open /management/ Customers list and confirm Source column renders …
- [ ] Confirm "by …" appears when a customer.create audit actor exists
- [ ] Create a customer from management and see Manual source
- [ ] Export customers CSV includes lead_source / created_by columns
- [ ] Deploy and verify https://yonderfleet.com/api/health
```

Six steps, none checked, no CI. The plan was written; nothing records that any of it ran.
Verify: <https://github.com/jsteiml/MidTN/pull/24>

---

## 5. How we audited ourselves (the dropped findings)

An audit whose subject is *overclaiming* forfeits all credibility if it overclaims. So
after the first pass we re-verified every candidate against the **specific** evidence, and
removed the ones that did not survive. This section exists so you can check that we did.

- **`rick-chick/agrr#174`** appeared to be a catch: it claimed *"2969 tests passed"* and
  the aggregate CI showed a failure. On inspection, the failing job was `dispatch` (a
  deploy step); the `frontend-test` job the claim actually refers to **passed.** The claim
  was true. **Dropped** — and the entire claim-vs-CI signal was demoted to
  "needs manual review," never counted in the headline, because an *aggregate* CI failure
  does not tell you the *specific* claim was false.
- **`EffortlessMetrics/tokmd-swarm#257`** showed failing Rust jobs, but its required CI
  (`CI (Required)`) passed and the PR was never merged. Ambiguous, not a clean catch.
  **Dropped.**
- **`ericson-j-santos/reqsys…#674`** tripped an early revert heuristic — but it is a
  documentation PR, and the word "revert" appears only as advice: *"Revert the commit if
  any inaccuracy is found."* **Dropped**, and we tightened the rule to require an explicit
  `#N` reference before anything is scored as a revert.

Our first pass reported six catches. Two of the six did not survive. The four that remain
are the four above. That subtraction — re-checking a plausible claim against exact evidence
instead of a keyword or an aggregate — is the single most important thing an agent skips,
and the single most important thing a trust layer does for you automatically.

---

## 6. Threats to validity (read this before you cite the numbers)

We want this used, so we want its limits stated plainly.

1. **Sampling.** "Most-recent closed PRs by bot author" skews toward smaller public repos
   and away from enterprise/private usage, where CI discipline is likely higher. The 47%
   is a fact about *this public sample*, not a universal rate.
2. **"No recorded evidence" ≠ "not tested."** The agent or a human may have tested locally.
   The metric measures the *public, re-runnable record* — which is exactly what auditability
   requires and exactly what was absent.
3. **We did not re-execute test suites.** Ground truth is GitHub's recorded CI + merge
   state. This is conservative (it can only *under*-count problems), but it means we cannot
   speak to correctness beyond what the repo itself recorded.
4. **Aggregate CI is coarse.** A single head-commit conclusion mixes required and optional
   jobs; this is precisely why we do not count claim-vs-CI as a catch (see §5).
5. **Revert detection is conservative.** Requiring an explicit `#N` reference avoids false
   positives but misses genuine reverts that don't cite a number — so hard catches are a
   floor, not a ceiling.
6. **Small per-agent n.** 70 PRs per agent; per-agent hard-catch counts are illustrative,
   not precision estimates. Do not rank vendors on four events.

None of these soften the core, evidence-free-merge finding, which depends on none of the
catch heuristics: it is simply *merged, and the record contains nothing to re-run.*

---

## 7. Reproduce it

Everything needed is published: the harness (`agent_trust_audit.py`), the scored ledger
(`agent_trust_ledger.jsonl`, 560 rows), and this essay. To re-derive from scratch you need
only the GitHub CLI (`gh`) authenticated, and Python 3.

```bash
python agent_trust_audit.py \
  "app/devin-ai-integration,app/cursor,app/google-labs-jules,app/codegen-sh,\
app/factory-droid,app/ellipsis-dev,app/sourcery-ai,app/tembo" 70 my_ledger.jsonl
```

The window will differ (it always pulls the most-recent PRs), so your exact rows will not
match ours — but the method, the verdict rules, and the shape of the result will. To check
*our* specific claims, open the four PR links in §4; they are immutable. To spot-check the
ledger, each row carries `url`, `verdict`, `why`, the claim quote, and the checkbox/CI/revert
signals it was scored on.

**Ledger row schema (excerpt):**
```json
{"repo":"owner/name","pr":24,"agent_author":"app/cursor","url":"https://…/pull/24",
 "merged":true,"ci":"none","claim":null,"boxes_checked":0,"boxes_unchecked":6,
 "reverts":null,"verdict":"CAUGHT","why":"MERGED with an entirely UNCHECKED verification plan …"}
```

---

## 8. Conclusion

Agents are improving quickly at two things: writing code, and telling you the code works.
They are not, on this evidence, improving at leaving behind anything that lets you *check*
the second claim independently. Forty-seven percent of merged agent pull requests in our
sample left no verifiable record at all; a handful actively contradicted themselves; and
the only reason we can state four catches and not six is that we did to our own findings
what the agents did not do to theirs — re-verify against the specific evidence.

That re-verification is not a manual chore that has to scale linearly with agent output. It
can be a layer: signed receipts of what an agent claims, objective re-scoring of those
claims against re-runnable evidence after merge, and per-class trust that an agent *earns*
and can *lose*. That layer is what we build (SignalBrain / `govern-kit`), and — holding
ourselves to the standard of this essay — our own trust ledger is cryptographically
verifiable by anyone with stock `ssh-keygen`, no access to us required.

The point of publishing the method and the ledger is not to win an argument. It is so you
can disagree with us *with evidence.* Please do.

---

### Appendix — the four hard catches, at a glance

| Agent | Repo / PR | Recorded contradiction |
|---|---|---|
| Codegen | [score-phantom#2](https://github.com/Heisdawrld/score-phantom/pull/2) | merged a new engine (#1), then merged an "URGENT" revert of it |
| Devin | [H-Gripe#648](https://github.com/tanzanite2025/H-Gripe-Studio/pull/648) | merged a fix (#647), then reverted "two regressions from #647" |
| Devin | [skin-changer#10](https://github.com/5thDimension-Sean/skin-changer/pull/10) | four merges (#6–#9) "all crashed the game"; mass-reverted to #5 |
| Cursor | [MidTN#24](https://github.com/jsteiml/MidTN/pull/24) | merged a 6-step test plan, 0 boxes checked, 0 CI runs |

*Data collected from the GitHub public API. Repository owners named in links are third
parties who used these agents; the subject of this study is the agents, not the owners.*
