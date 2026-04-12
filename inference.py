import os
import time

import requests
from openai import OpenAI


API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN", "")
ENV_URL = os.getenv("ENV_URL", "http://localhost:7860")
START_TAG = "[START]"
STEP_TAG = "[STEP]"
END_TAG = "[END]"


def _safe_token(value: object) -> str:
    raw = str(value)
    cleaned = "".join(ch if (ch.isalnum() or ch in "._-:") else "_" for ch in raw).strip("_")
    return cleaned or "na"


def _log_start(run_id: str, task_id: str) -> None:
    print(f"{START_TAG} run_id={_safe_token(run_id)} task_id={_safe_token(task_id)}")


def _log_step(idx: int, action: str, reward: float | None = None, done: bool | None = None, note: str | None = None) -> None:
    parts = [f"idx={idx}", f"action={_safe_token(action)}"]
    if reward is not None:
        parts.append(f"reward={reward:.4f}")
    if done is not None:
        parts.append(f"done={done}")
    if note is not None:
        parts.append(f"note={_safe_token(note)}")
    print(f"{STEP_TAG} {' '.join(parts)}")


def _log_end(run_id: str, task_id: str, score: float, success: bool) -> None:
    print(
        f"{END_TAG} run_id={_safe_token(run_id)} task_id={_safe_token(task_id)} "
        f"score={score:.4f} success={success}"
    )


def _post_json(path: str, payload: dict) -> dict:
    response = requests.post(f"{ENV_URL}{path}", json=payload, timeout=20)
    response.raise_for_status()
    return response.json()


def _safe_llm_reflection() -> str:
    """Optional tiny reflection call using OpenAI client; failures are non-blocking."""
    if not HF_TOKEN:
        return "llm_skipped_no_token"

    try:
        client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "Return exactly one short token."},
                {"role": "user", "content": "incident_recovery"},
            ],
            max_tokens=4,
            temperature=0.0,
        )
        return response.choices[0].message.content.strip().replace(" ", "_")
    except Exception:
        return "llm_unavailable"


def run_task(task_id: str = "easy", max_steps: int = 20) -> dict:
    run_id = f"{task_id}-{int(time.time())}"
    _log_start(run_id, task_id)

    reflection = _safe_llm_reflection()
    _log_step(idx=0, action="llm_reflection", note=reflection)

    _post_json("/reset", {"task_id": task_id})

    final_info = {"score": 0.0, "success": False}
    for idx in range(1, max_steps + 1):
        payload = _post_json("/step", {"use_policy": True, "deterministic": True})

        reward = float(payload.get("reward", 0.0))
        done = bool(payload.get("done", False))
        action = payload.get("action", "na")
        _log_step(idx=idx, action=action, reward=reward, done=done)

        if done:
            final_info = payload.get("info", final_info)
            break

    score = float(final_info.get("score", 0.0) or 0.0)
    success = bool(final_info.get("success", False))
    _log_end(run_id, task_id, score, success)

    return {
        "run_id": run_id,
        "task_id": task_id,
        "score": score,
        "success": success,
    }


if __name__ == "__main__":
    task = os.getenv("TASK_ID", "easy")
    run_task(task_id=task)
