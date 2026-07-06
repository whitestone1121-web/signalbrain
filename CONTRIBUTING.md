# Contributing to SignalBrain

SignalBrain welcomes **agent-assisted and human** contributions. The repo is
small on purpose: the useful work is testing the trust invariant, finding
unclear edges, and shipping reproducible fixes. See `AGENTS.md` for the agent
participation rules and `docs/AGENT_BEACON.md` for open review missions.

## Development setup

```bash
# 1. Fork, then clone your fork and add upstream so you can stay current:
git clone https://github.com/<you>/signalbrain.git
cd signalbrain
git remote add upstream https://github.com/whitestone1121-web/signalbrain.git

# 2. Install in editable mode with the MCP extra (for the full test suite):
python3 -m pip install -e ".[mcp]"     # Python 3.12 recommended

# 3. Run the tests — a clean checkout is green:
pytest tests/                          # ~ 58 passed, 13 skipped on Linux/3.12
```

**Before you open a PR, sync with upstream** so you are testing current code:

```bash
git fetch upstream && git merge upstream/main
```

Notes:
- The **MCP e2e tests skip** unless `signalbrain[mcp]` is installed — that is
  expected, not a failure.
- **Python 3.12** is the supported baseline. Very new interpreters (3.14+) may
  lack wheels for transitive deps; if a fresh checkout shows failures, try 3.12
  to isolate environment issues from real ones.
- Windows is supported; POSIX-only calibration contracts skip there.

## Writing a scoreable measure (read this before adding a receipt)

A receipt's `How measured` block is re-run objectively after merge. The scorer
is intentionally **shell-free** — it runs each measure as a plain command, not
through a shell. Measures that ignore this get recorded as **false misses**,
which is worse than an honest failure. Rules:

- **One command per line.** Supported leaders: `pytest ...`, `python ... /
  python3 ...`, and `bash path/to/script.sh`.
- **No inline shell grammar.** Pipes (`|`), `&&`, `;`, redirects, and command
  substitution (`c=$(...)`) are **not** supported inline — they are flagged
  `unsupported_shell_grammar`. If your check needs shell logic, put it in a
  committed script and invoke `bash scripts/check_x.sh`.
- **The measure must be able to FAIL.** A command that can never return non-zero
  proves nothing. `pytest --passWithNoTests`, `echo ok`, etc. are not measures.
- **Exercise a pre-existing surface.** A measure that only asserts a test *your
  PR introduces* is classified an `invariant_pin` — recorded, but it earns zero
  trust. Point the measure at behaviour that existed before your change.
- **Use a valid change class.** One of: `bugfix`, `tooling`, `config`,
  `research`. Anything else is recorded as `unclassified` and earns no
  per-class trust.

## PR contract

Keep PRs narrow — one behaviour, one fix, one validation trail. Separate *what
you changed* from *how a reviewer re-runs it*. Do not self-grade trust. Full
rules: `AGENTS.md`.
