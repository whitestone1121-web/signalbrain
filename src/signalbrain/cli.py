"""sb — score receipts, read gates.

Core invariant: only byte-identical, human-merged receipts that objectively
re-run can increase earned trust.

  sb score <receipt.md ...> [--root .] [--ledger ledger.jsonl] [--ref origin/main]
                            [--rescore] [--allow-unmerged] [--timeout 180]
  sb gate  [--ledger ledger.jsonl] [--window N] [--by-class] [--recency-only]
  sb check <receipt.md> [--root .] [--ref origin/main]

Exit codes: score → 0 if every receipt scored (held or not — honest failure is a
result), 3 if any was refused by the merged-receipt guard; gate → 0 TRUST, 1 GATE;
check → the guard's own code (0/3/4/5).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import gate as gate_mod
from . import guard as guard_mod
from .scorer import ScoreConfig, score_receipt


def _cmd_score(args: argparse.Namespace) -> int:
    cfg = ScoreConfig(
        root=Path(args.root).resolve(),
        ledger_path=Path(args.ledger),
        merged_ref=args.ref,
        allow_unmerged=args.allow_unmerged,
        timeout_s=args.timeout,
        rescore=args.rescore,
    )
    refused = 0
    for receipt in args.receipts:
        result = score_receipt(Path(receipt), cfg)
        print(json.dumps(result))
        if result["status"] == "refused_guard":
            refused += 1
    return 3 if refused else 0


def _cmd_gate(args: argparse.Namespace) -> int:
    ledger = Path(args.ledger)
    env = None
    if args.recency_only:
        env = {gate_mod.RECENCY_GATE_ENV: "1"}
        if args.window:
            env[gate_mod.WINDOW_ENV] = str(args.window)
    if args.by_class:
        status = gate_mod.per_class(ledger, window=args.window or None, env=env)
        print(json.dumps(status, indent=2))
        return 0 if any(r.get("status") == "auto-merge ELIGIBLE" for r in status.values()) else 1
    allowed, verdict = gate_mod.widening_allowed(ledger, env=env if env is not None else None)
    print(json.dumps(verdict, indent=2))
    return 0 if allowed else 1


def _cmd_check(args: argparse.Namespace) -> int:
    result = guard_mod.check_merged(Path(args.root).resolve(), Path(args.receipt), merged_ref=args.ref)
    print(result.message, file=sys.stderr)
    return result.code


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="sb", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("score", help="objectively score merged receipts into the ledger")
    p.add_argument("receipts", nargs="+")
    p.add_argument("--root", default=".")
    p.add_argument("--ledger", required=True)
    p.add_argument("--ref", default="origin/main")
    p.add_argument("--rescore", action="store_true")
    p.add_argument("--allow-unmerged", action="store_true", help="supervised experiments only")
    p.add_argument("--timeout", type=int, default=180)
    p.set_defaults(fn=_cmd_score)

    p = sub.add_parser("gate", help="print trust gates; exit 0 TRUST / 1 GATE")
    p.add_argument("--ledger", required=True)
    p.add_argument("--window", type=int, default=0)
    p.add_argument("--by-class", action="store_true")
    p.add_argument("--recency-only", action="store_true")
    p.set_defaults(fn=_cmd_gate)

    p = sub.add_parser("check", help="merged-receipt guard only")
    p.add_argument("receipt")
    p.add_argument("--root", default=".")
    p.add_argument("--ref", default="origin/main")
    p.set_defaults(fn=_cmd_check)

    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
