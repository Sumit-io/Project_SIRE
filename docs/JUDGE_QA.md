# Judge Q&A

## Q1. Where is RL used?
SIRE uses RL-style loops: `reset`, `step`, reward shaping, terminal condition, and episode scoring.

## Q2. Is this dependent on an LLM API key?
No. LLM reflection is optional. If token is absent, inference continues in keyless mode.

## Q3. Did you use PyTorch?
Yes. Baseline policy model and tensor inference path are implemented in `sire_env/baseline_policy.py`.

## Q4. What can you show live?
1. Scenario reset and state initialization.
2. AI-driven step-by-step recovery decisions.
3. Real-time metric improvements and final score.
4. Strict tagged logs for evaluator compatibility.

## Q5. How production-ready is this?
Local Docker build and container endpoint checks are completed. Deployment checklist is documented in `docs/DEPLOYMENT.md`.

## Q6. What if no internet during demo?
Project still runs locally with keyless mode and deterministic policy path.
