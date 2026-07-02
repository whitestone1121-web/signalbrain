#!/usr/bin/env bash
# SignalBrain 60-second demo — run it yourself; every line of output is real.
#
#   pip install git+https://github.com/whitestone1121-web/signalbrain
#   bash demo/demo.sh
#
# Builds a scratch git repo, then walks the four beats:
#   1. an agent tries to score its own unmerged claim   -> refused
#   2. a batch of tautological pin receipts             -> recorded, zero trust
#   3. an honest failure                                -> recorded forever
#   4. ten claims that actually held                    -> auto-merge EARNED
set -euo pipefail

G='\033[0;32m'; R='\033[0;31m'; Y='\033[1;33m'; D='\033[2m'; N='\033[0m'
say()  { printf "\n${Y}▶ %s${N}\n" "$*"; }
run()  { printf "${D}\$ %s${N}\n" "$*"; }

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
REPO="$WORK/acme-app"
LEDGER="$REPO/.signalbrain/ledger.jsonl"
mkdir -p "$REPO/receipts"
git -C "$REPO" init -q -b main
git -C "$REPO" -c user.email=demo@acme -c user.name=demo commit -q --allow-empty -m init

receipt() { # stem, command
  cat > "$REPO/receipts/$1.md" <<EOF
# $1

## Compared
- branch: \`agent/change@demo\`
- baseline: \`main@demo\`
- date: \`$(date +%F)\`

## Change summary
An agent-authored change.

## Metric delta
| Metric | Baseline | Branch | Delta |
|---|---|---|---|
| works | no | yes | claimed |

### How measured
\`\`\`bash
$2
\`\`\`

## Verdict
\`improvement\`

## Confidence
0.9

## change_class

tooling
EOF
}

merge_all() { git -C "$REPO" add -A; git -C "$REPO" -c user.email=demo@acme -c user.name=demo commit -qm "$1"; }

say "1. An agent claims its work is done — and tries to score itself BEFORE anyone merged it"
receipt "0001-tooling-agent-self-credit" 'python3 -c "print(0)"'
run "sb score receipts/0001-tooling-agent-self-credit.md --root . --ledger .signalbrain/ledger.jsonl --ref HEAD"
sb score "$REPO/receipts/0001-tooling-agent-self-credit.md" --root "$REPO" --ledger "$LEDGER" --ref HEAD || true
printf "${R}   refused: unmerged claims cannot enter the ledger. No agent grades its own homework.${N}\n"

say "2. The agent gets sneaky: a batch of receipts measured only by tests it wrote itself"
for i in 1 2 3; do
  mkdir -p "$REPO/tests"
  echo "def test_pin_$i(): assert True" > "$REPO/tests/test_pin_$i.py"
  receipt "000$((i+1))-tooling-streak-$i" "pytest tests/test_pin_$i.py -q"
done
merge_all "agent streak batch"
for i in 1 2 3; do
  sb score "$REPO/receipts/000$((i+1))-tooling-streak-$i.md" --root "$REPO" --ledger "$LEDGER" --ref HEAD > /dev/null
done
run "sb score receipts/000*-tooling-streak-*.md ...   # all three 'pass'"
printf "   ledger now holds %s rows — every one classified: ${D}%s${N}\n" \
  "$(grep -c . "$LEDGER")" "$(grep -o '"claim_kind": "[a-z_]*"' "$LEDGER" | sort | uniq -c | tr -s ' ')"
run "sb gate --ledger .signalbrain/ledger.jsonl --by-class --window 10"
sb gate --ledger "$LEDGER" --by-class --window 10 || printf "   (no class has ANY trust-eligible claims)\n"
printf "${R}   three green results, ZERO earned trust: held-by-construction pins are recorded, never counted.${N}\n"

say "3. An honest failure — recorded forever, not hidden"
receipt "0005-tooling-overclaim" 'python3 -c "raise SystemExit(1)"'
merge_all "agent overclaim"
run "sb score receipts/0005-tooling-overclaim.md ..."
sb score "$REPO/receipts/0005-tooling-overclaim.md" --root "$REPO" --ledger "$LEDGER" --ref HEAD | python3 -m json.tool | grep -E 'held|errors' || true
printf "${R}   the agent said 0.9 confidence. The measurement said no. That gap is the product.${N}\n"

say "4. Trust is EARNED: ten claims that actually hold"
for i in $(seq 10 19); do
  receipt "00$i-tooling-real-win" 'python3 -c "print(0)"'
done
merge_all "ten real wins"
for i in $(seq 10 19); do
  sb score "$REPO/receipts/00$i-tooling-real-win.md" --root "$REPO" --ledger "$LEDGER" --ref HEAD > /dev/null
done
run "sb gate --ledger .signalbrain/ledger.jsonl --by-class --window 10"
sb gate --ledger "$LEDGER" --by-class --window 10 || true
printf "${G}   auto-merge ELIGIBLE — earned by track record, revocable by evidence. Autonomy is graduated, never granted.${N}\n"

printf "\n${D}Every rule you just watched exists because a real agent tried the move: github.com/whitestone1121-web/signalbrain/blob/main/docs/incidents/${N}\n"
