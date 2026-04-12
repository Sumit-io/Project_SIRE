#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

echo "[1/5] Compile check"
python3 -m py_compile app.py inference.py sire_env/*.py tasks/*.py

echo "[2/5] API health check"
if ! curl -sS http://localhost:7860/health >/tmp/sire_health.json 2>/dev/null; then
  echo "ERROR: API is not running on http://localhost:7860"
  echo "Start it with: uvicorn app:app --host 0.0.0.0 --port 7860"
  exit 1
fi

echo "[3/5] Inference tagged log check"
mkdir -p validation
ENV_URL=http://localhost:7860 TASK_ID=easy python3 inference.py > validation/pre_submit_inference.log

start_count=$(grep -c '^\[START\]' validation/pre_submit_inference.log || true)
step_count=$(grep -c '^\[STEP\]' validation/pre_submit_inference.log || true)
end_count=$(grep -c '^\[END\]' validation/pre_submit_inference.log || true)
non_tag_count=$( (grep -vE '^\[(START|STEP|END)\]' validation/pre_submit_inference.log || true) | sed '/^$/d' | wc -l)

if [[ "$start_count" -ne 1 || "$end_count" -ne 1 || "$step_count" -lt 1 || "$non_tag_count" -ne 0 ]]; then
  echo "ERROR: Tagged log format check failed"
  echo "START=$start_count STEP=$step_count END=$end_count NON_TAG=$non_tag_count"
  exit 1
fi

echo "[4/5] Demo endpoint check"
demo_code=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:7860/demo || true)
if [[ "$demo_code" != "200" ]]; then
  echo "ERROR: /demo returned $demo_code"
  exit 1
fi

echo "[5/5] Secret scan (lightweight)"
if grep -RInE '(github_pat_|token=|Authorization:|api[_-]?key)' . --exclude-dir=.venv --exclude-dir=__pycache__ --exclude='*.log' >/tmp/sire_secret_scan.txt; then
  echo "WARN: Potential secret patterns found. Review /tmp/sire_secret_scan.txt"
else
  echo "No obvious secret patterns detected"
fi

echo "PASS: Pre-submission checks completed"
