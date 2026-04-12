# SIRE

SIRE (Service Incident Response Environment) is an OpenEnv-style simulation for training and evaluating incident-response decision making.

## What This Project Delivers
1. A reproducible environment with `reset()`, `step(action)`, and `state()` semantics.
2. Reward and scoring logic to evaluate recovery quality.
3. A policy-driven run loop for deterministic and stochastic action selection.
4. A non-technical demo UI at `/demo` for judge-friendly explanations.

## Why It Matters
SIRE turns outage response from intuition-based handling into measurable, replayable behavior. Teams can test response strategies safely without touching production traffic.

## RL and AI Positioning
1. RL pattern is implemented through episodic interaction with rewards and terminal conditions.
2. PyTorch is used for the baseline policy model.
3. LLM/API-key usage is optional and non-blocking; SIRE works fully in keyless mode.

## Quick Start

### Local
```bash
cd /workspaces/Bug_bounty/SST_Hackathon/sire_round1
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 7860
```

### Run Inference
```bash
cd /workspaces/Bug_bounty/SST_Hackathon/sire_round1
ENV_URL=http://localhost:7860 TASK_ID=easy python3 inference.py
```

### Open Demo UI
1. Open `http://localhost:7860/demo`
2. Reset a scenario.
3. Use `AI Next Step` to run recovery decisions.
4. Observe score and success in real time.

## Docker
```bash
cd /workspaces/Bug_bounty/SST_Hackathon/sire_round1
docker build -t sire-round1:latest .
docker run --rm -p 7860:7860 sire-round1:latest
```

## API Endpoints
1. `GET /health`
2. `POST /reset`
3. `POST /step`
4. `GET /state`
5. `GET /tasks`
6. `GET /explain`
7. `GET /demo`

## Documentation Index
1. `docs/EXECUTIVE_SUMMARY.md`
2. `docs/ARCHITECTURE.md`
3. `docs/RL_AI_USAGE.md`
4. `docs/DEPLOYMENT.md`
5. `docs/DEMO_SCRIPT.md`
6. `docs/SUBMISSION_CHECKLIST.md`
7. `docs/SECURITY_SECRETS.md`
8. `docs/PROJECT_BRIEF.md`
9. `docs/JUDGE_QA.md`
10. `docs/PARTICIPANT_PROFILE.md`
11. `docs/PHASE_CLOSURE_STATUS.md`
12. `docs/HF_DEPLOYMENT_RUNBOOK.md`

## Submission Automation
Run pre-submission checks:
```bash
bash scripts/pre_submission_check.sh
```

Run HF predeploy checks:
```bash
bash scripts/hf_predeploy_check.sh
```

## Notes
1. Do not commit secrets (`PAT`, cookies, session tokens) into version control.
2. Use environment variables for all credentials.
