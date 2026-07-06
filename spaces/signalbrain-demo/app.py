from __future__ import annotations

import json
import tempfile
from pathlib import Path

import gradio as gr

from signalbrain.gate import per_class
from signalbrain.receipt import parse_receipt

SAMPLE_RECEIPT = """# 0001-tooling-demo

## Compared
- branch: `demo@abc`
- baseline: `origin/main@def`
- date: `2026-07-06`

## Change summary
Demonstrates receipt parsing without executing commands.

## Metric delta
| Metric | Baseline | Branch | Delta |
|---|---|---|---|
| demo | 0 | 1 | +1 |

### How measured
```bash
python3 -c "pass"
```

## Verdict
`improvement`

## Confidence
0.9

## change_class
tooling
"""


def validate_receipt(text: str) -> str:
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "0001-tooling-demo.md"
        path.write_text(text, encoding="utf-8")
        receipt = parse_receipt(path)
        if receipt is None:
            return json.dumps({"ok": False, "error": "receipt is missing required scoreable fields"}, indent=2)
        return json.dumps(
            {
                "ok": True,
                "stem": receipt.stem,
                "confidence": receipt.confidence,
                "verdict": receipt.verdict,
                "change_class": receipt.change_class,
                "measure_commands": len(receipt.commands),
                "measure_errors": receipt.measure_errors,
            },
            indent=2,
        )


def sample_gate() -> str:
    with tempfile.TemporaryDirectory() as td:
        ledger = Path(td) / "ledger.jsonl"
        rows = [
            {
                "receipt_id": f"00{i:02d}-tooling-demo",
                "claim": f"00{i:02d}-tooling-demo",
                "confidence": 0.9,
                "held": True,
                "scored_by": "measured",
                "change_class": "tooling",
                "verdict": "improvement",
                "measure_errors": [],
            }
            for i in range(10)
        ]
        ledger.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
        return json.dumps(per_class(ledger, window=10), indent=2)


with gr.Blocks(title="SignalBrain Demo") as demo:
    gr.Markdown("# SignalBrain Demo\nValidate receipt shape and inspect a synthetic trust gate.")
    receipt_input = gr.Textbox(value=SAMPLE_RECEIPT, lines=24, label="Receipt markdown")
    receipt_output = gr.Code(label="Parsed receipt", language="json")
    gr.Button("Validate receipt").click(validate_receipt, inputs=receipt_input, outputs=receipt_output)
    gate_output = gr.Code(label="Sample gate", language="json")
    gr.Button("Show sample gate").click(sample_gate, outputs=gate_output)

if __name__ == "__main__":
    demo.launch()
