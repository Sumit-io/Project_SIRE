# Submission Checklist

## A. Code and Runtime
1. `python3 -m py_compile app.py inference.py sire_env/*.py tasks/*.py` passes.
2. `GET /health` returns 200.
3. `GET /demo` loads correctly.
4. `POST /reset` and `POST /step` work for easy, medium, hard.

## B. Inference Compliance
1. `inference.py` emits strict tagged logs:
2. `[START] ...`
3. `[STEP] ...`
4. `[END] ...`
5. No extra non-tag lines in stdout.

## C. Documentation
1. `README.md` updated and accurate.
2. `docs/` folder contains architecture, RL/AI usage, deployment, demo script.
3. Non-technical explanation available via `/explain` and demo UI.

## D. Containerization
1. Docker image builds successfully.
2. Container runs and serves health + demo endpoints.
3. Port mapping validated locally.

## E. Security and Secrets
1. No PAT, cookies, or session tokens inside project files.
2. No secrets hardcoded in source.
3. Use environment variables for tokens.

## F. Final Submission Artifacts
1. Public GitHub repository URL.
2. Hugging Face Space URL.
3. Short demo script and validation evidence files from `validation/`.
4. Participant details attached from `docs/PARTICIPANT_PROFILE.md`.

## G. Publication Helpers
1. `scripts/pre_submission_check.sh`
2. `scripts/hf_predeploy_check.sh`
3. `scripts/github_publish_safe.sh` (requires env vars)
4. `scripts/hf_space_publish_safe.sh` (requires env vars)
5. `scripts/scaler_gate_check.sh` (full disqualification checklist gate report)
