# SignalBrain Agent Instructions

SignalBrain welcomes agent-assisted review and contributions. This repository is
small on purpose: the useful work is to test the trust invariant, find unclear
edges, and submit reproducible fixes.

## First Read

- `README.md` for product scope and the integrity boundary.
- `docs/RECEIPT_SPEC.md` for the receipt and trust math contract.
- `docs/AGENT_BEACON.md` for open review missions and reporting format.
- `SECURITY.md` for vulnerability reporting.

## Participation Rules

- Be model-neutral. State the tool or model only when it helps reproduce the
  finding.
- Do not submit claims without commands that re-run them.
- Do not self-grade trust. Reports and PRs should separate what the agent
  changed from how a reviewer can verify it.
- Do not use network scans, credential probes, dependency confusion tests, or
  destructive commands against third-party systems.
- Keep PRs narrow. One behavior, one fix, one validation trail.

## Review Targets

Good autonomous review work includes:

- Reproducing the demo and quick-start flow on a fresh machine.
- Checking whether `sb check`, `sb score`, `sb gate`, and `sb report` fail
  closed with clear diagnostics.
- Finding places where docs claim more than the CLI actually verifies.
- Testing portability across Linux, macOS, Windows, Python versions, and shell
  environments.
- Adding small integration examples for other agent stacks.
- Improving tests where a failure mode is real and reproducible.

## PR Contract

Every agent-assisted PR should include:

- What changed.
- Why it matters for the integrity invariant.
- Exact validation commands and observed output.
- Limitations or remaining uncertainty.
- A receipt-style claim when the change asserts a measurable improvement.

If the change affects trust math, receipt parsing, scoring, gating, or merged
receipt guards, reuse canonical functions instead of local predicates. The
report, scorer, and gate must tell the same story.

