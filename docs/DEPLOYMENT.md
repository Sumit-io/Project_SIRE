# Deployment Guide

## Local API Deployment
```bash
cd /workspaces/Bug_bounty/SST_Hackathon/sire_round1
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 7860
```

## Local Validation
```bash
curl http://localhost:7860/health
curl http://localhost:7860/explain
curl -I http://localhost:7860/demo
```

## Docker Deployment
```bash
cd /workspaces/Bug_bounty/SST_Hackathon/sire_round1
docker build -t sire-round1:latest .
docker run --rm -p 7860:7860 sire-round1:latest
```

## Hugging Face Spaces Readiness
1. Root files required: `app.py`, `requirements.txt`, `Dockerfile`, `openenv.yaml`, `inference.py`.
2. Set runtime env vars if needed: `API_BASE_URL`, `MODEL_NAME`, `HF_TOKEN`, `ENV_URL`.
3. Ensure health endpoint responds quickly.
4. Verify strict inference log format before final submit.

## Release Gate Checklist
1. Compile check passes.
2. Demo UI loads and runs scenario.
3. Inference run produces only START/STEP/END log lines.
4. Container build and runtime checks pass.
