# Hugging Face Deployment Runbook

## Goal
Deploy SIRE to Hugging Face Spaces and verify API plus demo endpoints.

## Prerequisites
1. Hugging Face account and Space access.
2. Repository with cleaned secrets.
3. Required root files available: `app.py`, `inference.py`, `openenv.yaml`, `requirements.txt`, `Dockerfile`.

## Environment Variables (if needed)
1. `API_BASE_URL`
2. `MODEL_NAME`
3. `HF_TOKEN` (optional for LLM reflection)
4. `ENV_URL` (for local inference usage)

## Deploy Steps
1. Push code to GitHub repository.
2. Connect Space to repository or push directly to Space.
3. Configure Space runtime and secrets.
4. Wait for build completion.

## Post-Deploy Verification
1. `GET /health` returns 200.
2. `GET /demo` returns 200 and UI loads.
3. `GET /explain` returns plain-language summary.
4. Run `inference.py` against deployed URL and verify tagged logs.

## Failure Recovery
1. Check Space build logs for missing dependency or startup command.
2. Verify `requirements.txt` versions are compatible.
3. Confirm no hardcoded local URLs for production usage.
