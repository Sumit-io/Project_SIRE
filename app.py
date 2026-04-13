from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from sire_env.baseline_policy import choose_action, load_policy
from sire_env.environment_core import SireEnvironment
from tasks.task_definitions import TASKS, TASK_GRADERS, TASK_SUMMARY, build_tasks_with_graders


class ResetRequest(BaseModel):
    task_id: str = Field(default="easy", description="easy | medium | hard")


class StepRequest(BaseModel):
    action: Optional[str] = None
    use_policy: bool = True
    deterministic: bool = True


app = FastAPI(title="SIRE OpenEnv API", version="1.0.0")
env = SireEnvironment()
policy = load_policy()
FRONTEND_DIR = Path(__file__).resolve().parent / "frontend"

if FRONTEND_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIR)), name="assets")


@app.get("/")
def root() -> dict:
    return {
        "message": "SIRE environment is running.",
        "endpoints": ["/reset", "/step", "/state", "/tasks", "/explain", "/health", "/demo"],
    }


@app.get("/demo")
def demo() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/tasks")
def tasks() -> dict:
    return {
        "tasks": build_tasks_with_graders(),
        "task_configs": TASKS,
        "graders": TASK_GRADERS,
        "task_count": len(TASKS),
        "grader_count": len(TASK_GRADERS),
    }


@app.get("/explain")
def explain() -> dict:
    """Plain-language explanation so non-technical reviewers can understand project value."""
    return {
        "project_plain": {
            "what_it_does": "SIRE simulates major app incidents and helps an AI agent learn safer, faster recovery decisions.",
            "why_it_matters": "When popular apps fail, users lose trust and businesses lose money; faster recovery reduces both impact and stress.",
            "who_it_helps": [
                "Everyday app users",
                "Customer support teams",
                "Operations and reliability teams",
                "Product and business owners",
            ],
            "daily_life_examples": [
                "Payment flow fails during checkout",
                "Ride booking is slow during peak hours",
                "Login and search fail after a risky release",
            ],
        },
        "tasks_plain": TASK_SUMMARY,
        "actions_plain": {
            "prioritize_incident": "Focus on the highest-impact issue first.",
            "query_diagnostics": "Collect deeper signals before acting.",
            "apply_runbook_step": "Execute known safe recovery steps.",
            "rollback_release": "Revert a risky release that may have caused failures.",
            "escalate_oncall": "Bring in a senior responder when needed.",
            "mark_resolved": "Close incident only when health is truly restored.",
        },
    }


@app.post("/reset")
def reset(payload: Optional[ResetRequest] = None) -> dict:
    task_id = payload.task_id if payload is not None else "easy"
    return env.reset(task_id=task_id)


@app.get("/state")
def state() -> dict:
    return env.state()


@app.post("/step")
def step(payload: StepRequest) -> dict:
    action = payload.action

    if action is None and payload.use_policy:
        state_vector = env.current_state.to_vector()
        action = choose_action(policy, state_vector, deterministic=payload.deterministic)

    if action is None:
        return {
            "error": "action is required when use_policy=false",
            "hint": "pass an action or set use_policy=true",
        }

    return env.step(action)
