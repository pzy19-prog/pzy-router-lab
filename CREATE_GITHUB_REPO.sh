#!/usr/bin/env bash
set -euo pipefail

if ! command -v gh >/dev/null 2>&1; then
  echo 'GitHub CLI (gh) is required. Install gh and run: gh auth login' >&2
  exit 1
fi
gh auth status >/dev/null
python -m unittest discover -s tests -v
[ ! -d .git ] || { echo 'A Git repository already exists here; inspect before running.' >&2; exit 1; }
git init -b main
git add .
git commit -m 'chore: initialize local-first Router Lab experimental baseline'
gh repo create pzy-router-lab --public --description 'Local-first, replaceable task-routing benchmark lab' --source=. --remote=origin --push
printf '\nRepository: https://github.com/%s/pzy-router-lab\n' "$(gh api user --jq .login)"
