"""Merged-receipt guard — only human-merged receipts may be scored (SPEC §2, §6.4).

Python port of neural-chat-v3's `calibration_receipt_merged_check.sh`, keeping
its exit-code contract. Fail-closed: a missing ref blocks instead of passing.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

OK = 0
UNMERGED = 3
CONTENT_DRIFT = 4
REF_UNAVAILABLE = 5


@dataclass
class GuardResult:
    code: int
    message: str

    @property
    def ok(self) -> bool:
        return self.code == OK


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)


def check_merged(
    root: Path,
    receipt: Path,
    *,
    merged_ref: str = "origin/main",
    allow_unmerged: bool = False,
) -> GuardResult:
    """The receipt must exist on ``merged_ref`` with byte-identical content."""
    if allow_unmerged:
        return GuardResult(OK, "allow_unmerged set — merged-receipt guard skipped (supervised only)")

    if _git(root, "rev-parse", "--verify", "--quiet", f"{merged_ref}^{{commit}}").returncode != 0:
        return GuardResult(
            REF_UNAVAILABLE,
            f"ref '{merged_ref}' unavailable — fetch first, or pass allow_unmerged (supervised only)",
        )

    try:
        rel = receipt.resolve().relative_to(root.resolve())
    except ValueError:
        return GuardResult(UNMERGED, f"{receipt} is outside the repo — score only human-merged receipts")

    if _git(root, "cat-file", "-e", f"{merged_ref}:{rel}").returncode != 0:
        return GuardResult(UNMERGED, f"{rel} is not on {merged_ref} — score only human-merged receipts")

    local = _git(root, "hash-object", str(receipt)).stdout.strip()
    merged = _git(root, "rev-parse", f"{merged_ref}:{rel}").stdout.strip()
    if local != merged:
        return GuardResult(
            CONTENT_DRIFT,
            f"{rel} differs from the merged content on {merged_ref} — refusing to score a modified copy",
        )
    return GuardResult(OK, f"{rel} verified against {merged_ref}")
