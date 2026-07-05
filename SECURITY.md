# Security Policy

SignalBrain is integrity infrastructure. Please do not report vulnerabilities
through public issues until we have had a chance to investigate.

## Reporting

Email security issues to alan@signalbrain.ai with:

- affected package version or commit SHA
- a minimal reproduction
- whether the issue can let an unmerged, modified, self-scored, or test-only
  claim increase earned trust
- any logs or receipts needed to reproduce the behavior

We will acknowledge reports within 3 business days and will coordinate fixes
and disclosure timing with the reporter.

## Supported Versions

`signalbrain` is currently `0.x` alpha software. Security fixes target the
latest published release and `main`. Production pilots should pin exact package
versions and upgrade deliberately.

## Scope

In scope:

- bypasses of the merged-receipt guard
- ways to mutate earned trust without objective re-score
- ledger, pin-classification, or gate bugs that grant trust incorrectly
- command-injection or path traversal in receipt scoring

Out of scope:

- claims that are wrong because the user's receipt measured the wrong thing
- third-party CI, package-index, model, or infrastructure compromise
- GPU, kernel, or application-runtime memory corruption outside SignalBrain's
  receipt and ledger surfaces

## Secrets

Do not include tokens, private keys, or proprietary receipts in a report. If a
private artifact is needed, describe it first and we will arrange a safer
transfer path.
