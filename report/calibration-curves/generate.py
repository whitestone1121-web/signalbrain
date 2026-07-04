#!/usr/bin/env python3
"""Calibration curves from a SignalBrain ledger — the first deliverable of the
"online evaluation with stakes" report (H. Husain's framing).

Reads a measured ledger, joins each row to its receipt file (for the
measure-command difficulty proxy), and emits:

  - reliability.png        stated confidence vs observed hold-rate (overall)
  - by_class.png           the same, per change-class
  - by_difficulty.png      hold-rate by measure-command count (difficulty proxy)
  - bins.json              every number behind the plots

Reproduce (from a checkout of the reference deployment):
  python generate.py <ledger.jsonl> <receipts_dir> <out_dir>

Method notes (honesty first):
  - pins and non-measured rows are excluded, same as the trust gate
  - n is small at this stage; every bin is annotated with its count —
    read the counts before the curves
  - difficulty proxy = number of executable measure commands in the receipt;
    crude, disclosed, and step one of the stratification Hamel proposed
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from signalbrain.ledger import filter_rows, load_rows  # noqa: E402
from signalbrain.receipt import extract_commands_with_env  # noqa: E402

BINS = [(0.80, 0.85), (0.85, 0.90), (0.90, 0.95), (0.95, 1.01)]
FG, BG, ACC, RED, MUT = "#eef2f7", "#0d1117", "#34d399", "#f87171", "#94a3b8"


def style(ax, title):
    ax.set_facecolor(BG)
    ax.figure.set_facecolor(BG)
    for s in ax.spines.values():
        s.set_color("#2a2f3a")
    ax.tick_params(colors=MUT)
    ax.set_title(title, color=FG, fontsize=11)
    ax.xaxis.label.set_color(MUT)
    ax.yaxis.label.set_color(MUT)


def binned(rows):
    out = []
    for lo, hi in BINS:
        sub = [r for r in rows if lo <= float(r.get("confidence", 0)) < hi]
        held = sum(1 for r in sub if r.get("held"))
        out.append({
            "bin": f"[{lo:.2f},{min(hi,1.0):.2f})",
            "mid": (lo + min(hi, 1.0)) / 2,
            "n": len(sub),
            "held": held,
            "hold_rate": round(held / len(sub), 3) if sub else None,
        })
    return out


def main(ledger_path: Path, receipts_dir: Path, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = filter_rows(load_rows(ledger_path), require_measured=True)

    # difficulty proxy: measure-command count from the receipt file
    for r in rows:
        rid = str(r.get("receipt_id") or r.get("claim") or "")
        f = receipts_dir / f"{rid}.md"
        if f.is_file():
            _, cmds = extract_commands_with_env(f.read_text(encoding="utf-8"))
            r["_n_cmds"] = len(cmds)
        else:
            r["_n_cmds"] = None

    result = {"total_measured_rows": len(rows), "overall": binned(rows), "by_class": {}, "by_difficulty": {}}

    # 1. overall reliability
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    b = result["overall"]
    xs = [x["mid"] for x in b if x["n"]]
    ys = [x["hold_rate"] for x in b if x["n"]]
    ns = [x["n"] for x in b if x["n"]]
    ax.plot([0.8, 1.0], [0.8, 1.0], "--", color=MUT, lw=1, label="perfect calibration")
    ax.plot(xs, ys, "o-", color=ACC, lw=2, ms=7)
    for x, y, n in zip(xs, ys, ns):
        ax.annotate(f"n={n}", (x, y), textcoords="offset points", xytext=(6, -14), color=MUT, fontsize=8)
    ax.set_xlabel("stated confidence (bin midpoint)")
    ax.set_ylabel("observed hold-rate")
    ax.set_ylim(0, 1.05)
    style(ax, "Reliability: stated confidence vs measured hold-rate (all measured claims)")
    ax.legend(facecolor=BG, labelcolor=FG, edgecolor="#2a2f3a", fontsize=8)
    fig.tight_layout(); fig.savefig(out_dir / "reliability.png", dpi=150); plt.close(fig)

    # 2. per-class
    classes = sorted({str(r.get("change_class") or "unclassified") for r in rows})
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    ax.plot([0.8, 1.0], [0.8, 1.0], "--", color=MUT, lw=1)
    palette = [ACC, "#7cc0ff", "#f0b849", RED, "#bf5af2", MUT]
    for i, c in enumerate(classes):
        crows = [r for r in rows if str(r.get("change_class") or "unclassified") == c]
        cb = binned(crows)
        result["by_class"][c] = {"n": len(crows), "bins": cb}
        xs = [x["mid"] for x in cb if x["n"]]
        ys = [x["hold_rate"] for x in cb if x["n"]]
        if xs:
            ax.plot(xs, ys, "o-", lw=1.6, ms=5, label=f"{c} (n={len(crows)})", color=palette[i % len(palette)])
    ax.set_xlabel("stated confidence (bin midpoint)"); ax.set_ylabel("observed hold-rate"); ax.set_ylim(0, 1.05)
    style(ax, "Reliability by change-class")
    ax.legend(facecolor=BG, labelcolor=FG, edgecolor="#2a2f3a", fontsize=8)
    fig.tight_layout(); fig.savefig(out_dir / "by_class.png", dpi=150); plt.close(fig)

    # 3. difficulty proxy: measure-command count
    strata = {"1 command": [r for r in rows if r["_n_cmds"] == 1],
              "2+ commands": [r for r in rows if (r["_n_cmds"] or 0) >= 2],
              "receipt missing": [r for r in rows if r["_n_cmds"] is None]}
    fig, ax = plt.subplots(figsize=(6.5, 4.0))
    labels, rates, ns = [], [], []
    for k, sub in strata.items():
        held = sum(1 for r in sub if r.get("held"))
        rate = held / len(sub) if sub else 0
        result["by_difficulty"][k] = {"n": len(sub), "held": held, "hold_rate": round(rate, 3) if sub else None}
        labels.append(f"{k}\nn={len(sub)}"); rates.append(rate); ns.append(len(sub))
    bars = ax.bar(labels, rates, color=[ACC, "#7cc0ff", MUT], width=0.55)
    for bar, r in zip(bars, rates):
        ax.annotate(f"{r:.0%}", (bar.get_x() + bar.get_width() / 2, r), ha="center", va="bottom", color=FG, fontsize=10)
    ax.set_ylabel("hold-rate"); ax.set_ylim(0, 1.1)
    style(ax, "Hold-rate by difficulty proxy (measure-command count)")
    fig.tight_layout(); fig.savefig(out_dir / "by_difficulty.png", dpi=150); plt.close(fig)

    (out_dir / "bins.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ("total_measured_rows", "overall")}, indent=2))


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))
