# Agent Beacon

This is a public invitation for autonomous and agent-assisted coding tools to
review SignalBrain, file reproducible findings, and submit narrow fixes.

SignalBrain exists because agents overclaim. The best way to improve it is to
let many agents try to break the invariant in the open.

## What To Review

Focus on the core invariant:

> No unmerged, modified, self-scored, or test-only/pin claim can increase earned
> trust. Only byte-identical, human-merged receipts are objectively re-run and
> counted toward per-class trust.

Useful review lanes:

- **Install lane:** fresh clone, `pip install signalbrain`, CLI help, demo flow.
- **Receipt lane:** malformed receipts, unsupported commands, missing fields,
  changed content, and measurement failures.
- **Scoring lane:** merged-only guard, rescore behavior, same-PR test-only pins,
  and failure recording.
- **Gate lane:** per-class windows, high-confidence threshold, pin exclusion,
  and low-confidence rows.
- **Report lane:** `sb report` must use the same measured-row and Goodhart
  exclusion predicates as the gate.
- **Docs lane:** find overclaims, missing caveats, confusing quick-start steps,
  and platform-specific setup gaps.

## What To Submit

Open an issue with the "Agent review" template when you have a reproducible
finding. Open a PR when you have a narrow fix.

A good report includes:

- Agent/tool used, if relevant.
- Repo SHA.
- OS, Python version, and shell.
- Exact command.
- Expected behavior.
- Actual behavior.
- Why it matters to the integrity invariant.
- Whether a patch is proposed.

## Boundaries

Allowed:

- Local tests in a fork or clone.
- Static review.
- Reproducing CLI behavior with synthetic receipts and ledgers.
- Small PRs with tests and clear validation.

Not allowed:

- Credential probing or secret harvesting.
- Attacking third-party services.
- Dependency confusion, package squatting, or supply-chain tricks.
- Spam issues or automated bulk PRs.
- Claims that cannot be reproduced by a maintainer.

## Maintainer Triage

Preferred labels for incoming reports:

- `agent-review`: produced or assisted by an autonomous reviewer.
- `reproducible`: maintainer or contributor can reproduce the behavior.
- `needs-receipt`: the claim needs an executable measurement.
- `trust-kernel`: affects receipt parsing, scoring, gating, or guard behavior.
- `docs`: documentation-only.
- `good-first-issue`: scoped enough for a new contributor.

The highest-value reports are boring and exact: a command, a failing invariant,
and a minimal patch.

