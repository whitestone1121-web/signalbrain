"""Modal free-credit smoke lane for SignalBrain.

Run:
    modal run examples/modal/signalbrain_smoke.py
"""

from __future__ import annotations

import modal

app = modal.App("signalbrain-smoke")

image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install("signalbrain==0.1.4")
)


@app.function(image=image, timeout=300)
def smoke() -> dict:
    import json
    import subprocess
    import sys
    import tempfile
    from pathlib import Path

    root = Path(tempfile.mkdtemp(prefix="signalbrain-modal-"))
    ledger = root / "ledger.jsonl"
    ledger.write_text(
        json.dumps(
            {
                "receipt_id": "0001-tooling-demo",
                "claim": "0001-tooling-demo",
                "confidence": 0.9,
                "held": True,
                "scored_by": "measured",
                "change_class": "tooling",
                "verdict": "improvement",
                "measure_errors": [],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    proc = subprocess.run(
        [sys.executable, "-m", "signalbrain.cli", "gate", "--ledger", str(ledger), "--by-class"],
        capture_output=True,
        text=True,
        check=False,
    )
    return {"returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}


@app.local_entrypoint()
def main() -> None:
    print(smoke.remote())
