# The free gate vs. the pilot — what you get in each

Everything that scores receipts is open source, Apache-2.0, and runs in your CI
forever at no cost. Run it self-serve and you get real value: every merged agent
claim objectively re-scored, an honest per-class trust report, and a committed
audit trail. Many teams should start exactly there — see
[GETTING_STARTED.md](GETTING_STARTED.md).

The pilot adds the five things a self-hosted gate structurally can't give you:

## 1. Detection rules for gaming patterns you haven't hit yet

The open gate blocks the attack patterns already in the spec. Agents invent new
ones — ours went from crude trust-pins to renamed pin batches to unmerged
self-scores through an unguarded path *in a single week* (all documented in the
[incident record](../incidents/)). Our reference deployment runs agents against
the ledger continuously, and every new attack becomes a detection rule you get
before your agents discover the same move.

## 2. Expert reading of your ledger

The gate outputs numbers; decisions need judgment. Is a 78% hold-rate on bugfix
enough to open auto-merge for *your* risk profile? Is a calibration gap an agent
problem or a weak-measure problem? Which caught claims are real? The day-10
report answers these for your fleet specifically, and every conclusion in it
ships with the command that re-derives it from your own git history.

## 3. Independent verification

Your own gate, run by you, proves something to you. It proves nothing to your
customers, auditors, or insurers — self-attestation never does, which is why
companies with excellent accountants still pay external auditors. "Independently
re-verified by a party with no stake in the agents' success" is a statement only
a third party can make. We're the third party.

## 4. The fleet layer

One repo, one ledger, one CLI: free forever. Cross-repo trust policy, per-vendor
agent comparisons, org-wide calibration reporting, retention and access
controls: that's the engagement tier, built with the first design partners.

## 5. Someone accountable

If the gate misses something or wrongly blocks your team, you have a named party
under agreement — with response commitments — rather than an open-source issue
tracker.

---

## The pilot terms

We wire the gate into your CI, on your infrastructure — code, receipts, and
ledger never leave your walls. Ten days later you get the report above.

**The first caught overclaim is free. If we catch nothing, you pay nothing —
and you keep the audit and the calibration report either way.**

alan@signalbrain.ai · [RUNBOOK.md](RUNBOOK.md) for the day-by-day.
