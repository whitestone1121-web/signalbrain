"""Same-PR test-only pin detection (SPEC §6.2).

A receipt whose measure section runs ONLY tests introduced by the receipt's own
merge commit holds by construction — it is recorded as an invariant pin, never
as trust. Port of neural-chat-v3 `calibration_same_pr_pin` (shipped in the
#1196 remediation); a copy also lives under ``signalbrain.governance`` — this
module is the packaged surface and the two consolidate in the Phase-0 refactor.

Deliberately narrow: if ANY measure command is not pytest, or ANY pytest target
existed before the receipt's merge commit, the receipt is NOT a pin — receipts
for genuine behavioral changes that are verified partly by pre-existing tests
must keep earning trust (see the over-pinning finding in the founding incident).
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

_NODE_DEF = re.compile(r"^\+\s*(?:async\s+)?def\s+(test_\w+)")


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)


def receipt_merge_commit(root: Path, receipt_rel: str, ref: str) -> str | None:
    proc = _git(root, "log", "--diff-filter=A", "-1", "--format=%H", ref, "--", receipt_rel)
    sha = proc.stdout.strip()
    if sha:
        return sha
    proc = _git(root, "log", "-1", "--format=%H", ref, "--", receipt_rel)
    return proc.stdout.strip() or None


def file_exists_at(root: Path, commit: str, relpath: str) -> bool:
    return _git(root, "cat-file", "-e", f"{commit}:{relpath}").returncode == 0


def node_introduced_in_diff(root: Path, parent: str, commit: str, relpath: str, node: str) -> bool:
    proc = _git(root, "diff", parent, commit, "--", relpath)
    if proc.returncode != 0:
        return False
    for line in proc.stdout.splitlines():
        match = _NODE_DEF.match(line)
        if match and match.group(1) == node:
            return True
    return False


def _is_pytest_argv(argv: list[str]) -> bool:
    if argv and argv[0] == "pytest":
        return True
    return (
        len(argv) >= 3
        and argv[0] in ("python3", "python", sys.executable)
        and argv[1] == "-m"
        and argv[2] == "pytest"
    )


def _pytest_args(argv: list[str]) -> list[str]:
    if argv[0] == "pytest":
        return argv[1:]
    if _is_pytest_argv(argv):
        return argv[3:]
    return []


def parse_pytest_targets(commands: list[list[str]]) -> list[tuple[str, str | None]]:
    targets: list[tuple[str, str | None]] = []
    for argv in commands:
        if not _is_pytest_argv(argv):
            continue
        for token in _pytest_args(argv):
            if token.startswith("-"):
                continue
            if not (token.endswith(".py") or ".py::" in token):
                continue
            if "::" in token:
                path, node = token.split("::", 1)
                targets.append((path, node.split("[", 1)[0]))
            else:
                targets.append((token, None))
    return targets


def is_same_pr_test_only_pin(
    root: Path,
    receipt_rel: str,
    commands: list[list[str]],
    *,
    merged_ref: str = "origin/main",
) -> bool:
    if not commands or not all(_is_pytest_argv(argv) for argv in commands):
        return False
    targets = parse_pytest_targets(commands)
    if not targets:
        return False
    merge_commit = receipt_merge_commit(root, receipt_rel, merged_ref.strip())
    if not merge_commit:
        return False
    parent_proc = _git(root, "rev-parse", f"{merge_commit}^")
    if parent_proc.returncode != 0:
        return False
    parent = parent_proc.stdout.strip()
    for relpath, node in targets:
        if node:
            if not node_introduced_in_diff(root, parent, merge_commit, relpath, node):
                return False
        elif file_exists_at(root, parent, relpath):
            return False
    return True
