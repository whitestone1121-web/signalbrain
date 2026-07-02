# Design partner outreach — v1 (copy to Gmail)

**Subject:** We caught our own AI agent faking its trust score — want to audit yours?

---

Hi [Name],

I'm building the trust layer for AI-modified software: signed improvement receipts, objective re-score, and per-class earned autonomy. The question it answers is concrete — did the agent actually do what it claimed?

Last week our own autonomous dev lane tried to pad its calibration ledger to 100% tooling TRUST in a local working tree. The playbook: batch receipts whose only change was contract tests that pass by construction, plus an unmerged receipt scored through a guard bypass. It never reached git. We caught it between score and push, remediated in merged commits, and published the full incident record with SHAs and reproduce commands:

https://github.com/whitestone1121-web/neural-chat-v3/blob/main/docs/incidents/2026-07-tooling-trust-streak-gaming.md

Open receipt spec (v0.1):

https://github.com/whitestone1121-web/neural-chat-v3/blob/main/docs/RECEIPT_SPEC.md

SignalBrain package (trust layer extract):

https://github.com/whitestone1121-web/signalbrain

**The offer:** We score your coding agents' claims against what actually merged in your repo. First caught overclaim is free. If we don't find one, you don't pay — and you've still audited your agents. Either outcome is a deliverable.

Worth a 15-minute call to see if your CI/agent setup is a fit?

[Your name]
[LinkedIn / signalbrain.ai]
