#!/usr/bin/env bash
# Publish the current source tree to an already-created empty Git repository.
set -euo pipefail

repo_url="${1:-}"
if [[ -z "$repo_url" ]]; then
  echo "Usage: bash scripts/push-new-repo.sh <new-repository-url>"
  exit 1
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Run this script from inside the JanSetu Git repository."
  exit 1
fi

if ! git diff --cached --quiet; then
  echo "There are already staged changes. Review or commit them before running this script."
  exit 1
fi

# Add source changes, then remove previously tracked generated files from the
# new repository's index. `--cached` keeps every local file on disk.
git add -A
while IFS= read -r -d '' path; do
  case "$path" in
    __pycache__/*|*/__pycache__/*|.pytest_cache/*|venv/*|.venv/*|env/*|*.pyc|*.pyo|*.pyd|*.db|*.sqlite|*.sqlite3|.env)
      git rm --cached --ignore-unmatch -- "$path"
      ;;
  esac
done < <(git ls-files -z)

if ! git diff --cached --quiet; then
  git commit -m "Prepare JanSetu for publication"
fi

git branch -M main
if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "$repo_url"
else
  git remote add origin "$repo_url"
fi
git push -u origin main
