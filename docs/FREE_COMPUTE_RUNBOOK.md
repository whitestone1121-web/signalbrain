# Free Compute Runbook

SignalBrain should use free public compute where it improves reproducibility,
agent participation, or public demos. Free compute is not the source of truth:
`main`, release tags, PyPI, and human-reviewed PRs remain authoritative.

## Live In This Repository

### GitHub Actions

Workflow: `.github/workflows/ci.yml`

Use it for:

- Linux, Windows, and macOS package tests.
- Python 3.11, 3.12, 3.13, and 3.14 compatibility checks.
- Package build verification.
- Weekly drift detection.

Public repositories get free standard GitHub-hosted runner usage. Keep jobs
short, path-scoped when possible, and deterministic.

### GitHub Codespaces

Config: `.devcontainer/devcontainer.json`

Use it for:

- One-click contributor review.
- Agent-assisted repo exploration.
- Fresh-environment reproduction of issues.

The devcontainer installs SignalBrain with MCP extras and runs the package test
suite on creation.

## Ready To Deploy

### Cloudflare Workers

Path: `deploy/cloudflare/agent-beacon-worker/`

Use it for:

- `signalbrain.ai/agent-beacon` redirect to the GitHub beacon issue.
- `signalbrain.ai/agent-beacon.json` machine-readable review instructions.

Operator steps:

```bash
cd deploy/cloudflare/agent-beacon-worker
npm install
npx wrangler deploy
```

Required account state: Cloudflare login and domain route.

### Hugging Face Spaces

Path: `spaces/signalbrain-demo/`

Use it for:

- Public interactive receipt validation.
- Gate-status demos with synthetic ledgers.
- A safe demo that never executes user-supplied measure commands.

Operator steps:

```bash
huggingface-cli login
huggingface-cli repo create signalbrain-demo --type space --space_sdk gradio
cd spaces/signalbrain-demo
git init
git remote add origin https://huggingface.co/spaces/<user-or-org>/signalbrain-demo
git add .
git commit -m "initial signalbrain demo space"
git push -u origin main
```

Required account state: Hugging Face token with Space write access.

## Burst Evaluation Lanes

### Kaggle / Colab

Notebook: `notebooks/signalbrain_free_compute_quickstart.ipynb`

Use it for:

- Public reproducibility notebooks.
- Calibration curve experiments.
- Contributor-friendly walkthroughs.

Do not put secrets in notebooks. Treat notebook outputs as evidence candidates,
not authoritative release artifacts.

### Modal

Example: `examples/modal/signalbrain_smoke.py`

Use it for:

- Burst package smoke tests.
- Larger synthetic ledger/report runs.
- Short GPU or CPU experiments when free credits are available.

Operator steps:

```bash
pip install modal
modal setup
modal run examples/modal/signalbrain_smoke.py
```

Required account state: Modal account with available monthly credits.

### Lightning AI

Use the same commands as the Codespaces lane:

```bash
python -m pip install -e ".[mcp]" pytest
python -m pytest tests/ -q
```

Use it for GPU experiments or heavier notebooks when monthly credits are
available. Keep the Studio stopped when not in active use.

### Oracle Always Free

Use it only for low-risk background work:

- A self-hosted runner for public, non-secret, non-release jobs.
- Periodic beacon checks.
- Static mirrors or dashboards.

Do not place release credentials or PyPI publishing authority on an Always Free
VM. Keep GitHub Actions as the release runner.

## Guardrails

- No production secret should be required for a free-compute lane.
- A failing free-compute lane should block only the surface it owns.
- Public demos must not execute arbitrary user-supplied shell commands.
- Any claim produced by a notebook, Space, Worker, or external runner still
  needs a receipt and objective re-run before it affects trust.
