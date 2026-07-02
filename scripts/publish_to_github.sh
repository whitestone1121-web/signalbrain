#!/usr/bin/env bash
# Run from Lucy/WSL with full GitHub org permissions (cloud agent token cannot create repos).
set -euo pipefail
cd "$(dirname "$0")"
git branch -M main
gh repo create whitestone1121-web/signalbrain --public --source=. --remote=origin --push
echo "Published: https://github.com/whitestone1121-web/signalbrain"
