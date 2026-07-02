"""Skip tests that interrogate the reference deployment's git history or ledger.

This standalone repo ships the product code and its hermetic contracts; a
handful of extracted tests pin facts about neural-chat-v3 (Titan) history that
do not exist here. They remain meaningful only in the reference deployment.
"""

from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
_REFERENCE_CONTEXT = (REPO / "docs" / "calibration" / "improvement_claim_ledger.jsonl").is_file() and (
    REPO / "docs" / "improvements" / "0575-tooling-automerge-receipt-class-footer.md"
).is_file()

requires_reference_deployment = pytest.mark.skipif(
    not _REFERENCE_CONTEXT,
    reason="requires reference-deployment context (neural-chat-v3 ledger + receipt history)",
)


def pytest_collection_modifyitems(items):
    reference_files = {
        "test_calibration_same_pr_test_pin_contract.py",
        "test_calibration_antigoodhart_contract.py",
    }
    for item in items:
        if Path(str(item.fspath)).name in reference_files and not _REFERENCE_CONTEXT:
            item.add_marker(requires_reference_deployment)
