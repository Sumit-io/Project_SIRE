#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -d .git ]]; then
  echo "INFO: initializing git repository"
  git init
fi

if [[ -z "${GITHUB_REPO_URL:-}" ]]; then
  echo "ERROR: set GITHUB_REPO_URL (example: https://github.com/Sumit-io/Project_SIRE.git)"
  exit 1
fi

if [[ -z "${GITHUB_TOKEN:-}" ]]; then
  echo "ERROR: set GITHUB_TOKEN in environment"
  exit 1
fi

git add .

if git diff --cached --quiet; then
  echo "INFO: nothing to commit"
else
  git commit -m "Prepare SIRE for submission"
fi

if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "$GITHUB_REPO_URL"
else
  git remote add origin "$GITHUB_REPO_URL"
fi

branch=$(git rev-parse --abbrev-ref HEAD)
if [[ "$branch" == "HEAD" ]]; then
  branch=main
  git branch -M "$branch"
fi

# Use Basic auth header so PAT works with git-over-HTTPS without storing token in remote URL.
AUTH_B64="$(printf 'x-access-token:%s' "${GITHUB_TOKEN}" | base64 -w0)"
git -c http.extraHeader="Authorization: Basic ${AUTH_B64}" push -u origin "$branch"

echo "PASS: pushed to ${GITHUB_REPO_URL} on branch ${branch}"
