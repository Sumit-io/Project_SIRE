# Security and Secrets Handling

## Critical Rule
Never commit personal access tokens, cookies, or session identifiers to version control.

## What To Treat As Secret
1. GitHub PAT values.
2. Hugging Face session cookies.
3. Any `token`, `api_key`, `authorization` values.

## Safe Practice
1. Store secrets in local environment variables.
2. Keep `.env` files out of git.
3. Rotate exposed credentials immediately.

## Recommended Environment Variables
1. `HF_TOKEN`
2. `API_BASE_URL`
3. `MODEL_NAME`
4. `ENV_URL`
5. Optional: `GITHUB_TOKEN` for local git automation

## Pre-Push Safety Check
Run a quick scan before pushing:
```bash
grep -RInE "(github_pat_|hf_[A-Za-z0-9]|token=|Authorization:|api[_-]?key)" .
```

If anything sensitive appears, remove it and rotate the key.
