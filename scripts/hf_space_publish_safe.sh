#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

if [[ -z "${HF_USERNAME:-}" ]]; then
  echo "ERROR: set HF_USERNAME (example: sumit-io)"
  exit 1
fi

if [[ -z "${HF_SPACE_NAME:-}" ]]; then
  echo "ERROR: set HF_SPACE_NAME (example: project-sire)"
  exit 1
fi

if [[ -z "${HF_TOKEN:-}" ]]; then
  echo "ERROR: set HF_TOKEN"
  exit 1
fi

SPACE_REPO="spaces/${HF_USERNAME}/${HF_SPACE_NAME}"
REMOTE_URL="https://huggingface.co/${SPACE_REPO}"
AUTH_B64="$(printf '%s:%s' "$HF_USERNAME" "$HF_TOKEN" | base64 -w0)"

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

# Copy only submission-relevant files for Space runtime.
cp app.py inference.py openenv.yaml requirements.txt pyproject.toml uv.lock Dockerfile "$TMP_DIR/"
cp docs/HF_SPACE_README.md "$TMP_DIR/README.md"
cp -r sire_env tasks frontend server "$TMP_DIR/"

pushd "$TMP_DIR" >/dev/null

git init -q
git config user.email "${GIT_EMAIL:-sumit24073@gmail.com}"
git config user.name "${GIT_NAME:-Sumit Kumar}"
git checkout -b main >/dev/null 2>&1 || git branch -M main
git add .
git commit -m "Deploy SIRE to Hugging Face Space" >/dev/null

if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "$REMOTE_URL"
else
  git remote add origin "$REMOTE_URL"
fi

git -c http.extraHeader="Authorization: Basic ${AUTH_B64}" push -f origin main
popd >/dev/null

echo "PASS: deployed to ${REMOTE_URL}"
