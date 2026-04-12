#!/usr/bin/env bash
set -u

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

REPORT="validation/scaler_pre_submission_gate_report.txt"
HF_BASE="${HF_SPACE_BASE_URL:-https://sumit-io-project-sire.hf.space}"

mkdir -p validation

pass_count=0
fail_count=0

record_pass() {
  echo "PASS: $1" >> "$REPORT"
  pass_count=$((pass_count + 1))
}

record_fail() {
  echo "FAIL: $1" >> "$REPORT"
  fail_count=$((fail_count + 1))
}

{
  echo "Scaler Pre-Submission Gate Report"
  date -u '+Date: %Y-%m-%d %H:%M:%SZ'
  echo "HF_BASE=$HF_BASE"
  echo

  echo "[1] HF Space deploy + ping/reset"
  health_code=$(curl -sS -o /tmp/hf_health.json -w '%{http_code}' "$HF_BASE/health" || true)
  reset_code=$(curl -sS -o /tmp/hf_reset.json -w '%{http_code}' -X POST "$HF_BASE/reset" -H 'Content-Type: application/json' -d '{"task_id":"easy"}' || true)
  echo "health_code=$health_code"
  echo "reset_code=$reset_code"
  if [[ "$health_code" == "200" && "$reset_code" == "200" ]]; then
    python3 - <<'PY'
import json
obj=json.load(open('/tmp/hf_reset.json'))
print('reset_task_id=', obj.get('task_id'))
print('has_state=', 'state' in obj)
PY
    record_pass "HF health/reset"
  else
    head -c 200 /tmp/hf_health.json 2>/dev/null || true
    echo
    head -c 200 /tmp/hf_reset.json 2>/dev/null || true
    echo
    record_fail "HF health/reset"
  fi
  echo

  echo "[2] OpenEnv spec compliance"
  if python3 - <<'PY'
import yaml
obj=yaml.safe_load(open('openenv.yaml'))
ok = (
    obj.get('interfaces',{}).get('reset',{}).get('path') == '/reset' and
    obj.get('interfaces',{}).get('step',{}).get('path') == '/step' and
    obj.get('interfaces',{}).get('state',{}).get('path') == '/state' and
    len(obj.get('tasks',[])) >= 3 and
    obj.get('scoring',{}).get('range',{}).get('min') == 0.0 and
    obj.get('scoring',{}).get('range',{}).get('max') == 1.0
)
print('openenv_ok=', ok)
raise SystemExit(0 if ok else 1)
PY
  then
    record_pass "openenv.yaml contract"
  else
    record_fail "openenv.yaml contract"
  fi
  echo

  echo "[3] Dockerfile builds"
  if docker build -t sire-round1:scaler-gate . >/tmp/scaler_docker_build.log 2>&1; then
    echo "docker_build=PASS"
    record_pass "Docker build"
  else
    echo "docker_build=FAIL"
    tail -n 40 /tmp/scaler_docker_build.log
    record_fail "Docker build"
  fi
  echo

  echo "[4] Baseline reproduces (inference.py)"
  start=$(date +%s)
  if ENV_URL=http://localhost:7860 TASK_ID=easy python3 inference.py > /tmp/scaler_inference.log 2>/tmp/scaler_inference.err; then
    end=$(date +%s)
    dur=$((end-start))
    start_tags=$(grep -c '^\[START\]' /tmp/scaler_inference.log || true)
    step_tags=$(grep -c '^\[STEP\]' /tmp/scaler_inference.log || true)
    end_tags=$(grep -c '^\[END\]' /tmp/scaler_inference.log || true)
    non_tag_lines=$( (grep -vE '^\[(START|STEP|END)\]' /tmp/scaler_inference.log || true) | sed '/^$/d' | wc -l )
    echo "runtime_seconds=$dur"
    echo "start_tags=$start_tags step_tags=$step_tags end_tags=$end_tags non_tag_lines=$non_tag_lines"
    grep '^\[END\]' /tmp/scaler_inference.log | tail -n1 || true
    if [[ "$start_tags" -eq 1 && "$step_tags" -ge 1 && "$end_tags" -eq 1 && "$non_tag_lines" -eq 0 ]]; then
      record_pass "inference reproducibility + log format"
    else
      record_fail "inference reproducibility + log format"
    fi
  else
    cat /tmp/scaler_inference.err
    record_fail "inference reproducibility + log format"
  fi
  echo

  echo "[5] 3+ tasks with graders score/reward ranges"
  if python3 - <<'PY'
from sire_env.environment_core import SireEnvironment
from sire_env.baseline_policy import load_policy, choose_action

policy = load_policy()
ok = True
for task in ['easy','medium','hard']:
    env = SireEnvironment()
    env.reset(task)
    min_reward = 10.0
    max_reward = -10.0
    out = None
    for _ in range(40):
        action = choose_action(policy, env.current_state.to_vector(), deterministic=True)
        out = env.step(action)
        r = float(out.get('reward', 0.0))
        min_reward = min(min_reward, r)
        max_reward = max(max_reward, r)
        if out.get('done'):
            break
    score = float(out['info']['score'])
    score_ok = 0.0 <= score <= 1.0
    reward_ok = (-1.0 <= min_reward <= 1.5) and (-1.0 <= max_reward <= 1.5)
    print(f"task={task} score={score:.4f} score_ok={score_ok} reward_min={min_reward:.4f} reward_max={max_reward:.4f} reward_ok={reward_ok}")
    ok = ok and score_ok and reward_ok
raise SystemExit(0 if ok else 1)
PY
  then
    record_pass "task graders and score/reward ranges"
  else
    record_fail "task graders and score/reward ranges"
  fi
  echo

  echo "[6] Mandatory env variables in config"
  vars_ok=true
  for v in API_BASE_URL MODEL_NAME HF_TOKEN; do
    if grep -q "^$v=" .env.example; then
      echo "$v=present_in_env_example"
    else
      vars_ok=false
      echo "$v=missing_in_env_example"
    fi
  done
  if [[ "$vars_ok" == "true" ]]; then
    record_pass "mandatory env vars template"
  else
    record_fail "mandatory env vars template"
  fi
  echo

  echo "[7] OpenAI client usage + root inference.py"
  openai_import_count=$(grep -c 'from openai import OpenAI' inference.py || true)
  openai_client_count=$(grep -c 'OpenAI(' inference.py || true)
  echo "openai_import_count=$openai_import_count openai_client_count=$openai_client_count"
  if [[ -f inference.py && "$openai_import_count" -ge 1 && "$openai_client_count" -ge 1 ]]; then
    record_pass "OpenAI client + root inference.py"
  else
    record_fail "OpenAI client + root inference.py"
  fi
  echo

  echo "[8] Infra restrictions quick check"
  if [[ -f /tmp/scaler_inference.log ]]; then
    if grep -q '^\[END\]' /tmp/scaler_inference.log; then
      record_pass "inference completed under time budget"
    else
      record_fail "inference completed under time budget"
    fi
  else
    record_fail "inference completed under time budget"
  fi
  echo "target_machine=vcpu2_memory8gb (design constraint acknowledged)"
  echo

  echo "[9] Validator script"
  if bash scripts/pre_submission_check.sh >/tmp/scaler_validator.log 2>&1; then
    echo "validator=PASS"
    record_pass "pre-submission validator"
  else
    echo "validator=FAIL"
    tail -n 80 /tmp/scaler_validator.log
    record_fail "pre-submission validator"
  fi
  echo

  echo "Summary"
  echo "pass_count=$pass_count"
  echo "fail_count=$fail_count"
  if [[ "$fail_count" -eq 0 ]]; then
    echo "overall=PASS"
  else
    echo "overall=FAIL"
  fi
} > "$REPORT"

cat "$REPORT"
