#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

echo "[1/4] Required file check"
required=(app.py inference.py openenv.yaml requirements.txt Dockerfile)
for f in "${required[@]}"; do
  [[ -f "$f" ]] || { echo "ERROR: missing $f"; exit 1; }
done

echo "[2/4] Compile check"
python3 -m py_compile app.py inference.py sire_env/*.py tasks/*.py

echo "[3/4] Optional env visibility"
for v in API_BASE_URL MODEL_NAME HF_TOKEN ENV_URL; do
  if [[ -n "${!v:-}" ]]; then
    echo "$v=SET"
  else
    echo "$v=UNSET"
  fi
done

echo "[4/4] Local endpoint smoke (if running)"
health_code=$(curl -s -o /tmp/sire_hf_predeploy_health.json -w '%{http_code}' http://localhost:7860/health || true)
if [[ "$health_code" == "200" ]]; then
  echo "LOCAL_HEALTH_OK"
  demo_code=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:7860/demo || true)
  echo "LOCAL_DEMO_CODE=$demo_code"
else
  echo "INFO: local API not running on port 7860; skipping endpoint smoke"
fi

echo "PASS: HF predeploy check complete"
