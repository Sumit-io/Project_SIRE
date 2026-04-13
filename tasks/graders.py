from sire_env.evaluation_grader import EvaluationGrader
from sire_env.incident_state import IncidentState


def _state_from_dict(state: dict) -> IncidentState:
    return IncidentState(
        severity=int(state["severity"]),
        affected_services=int(state["affected_services"]),
        error_rate=float(state["error_rate"]),
        latency_p95_ms=float(state["latency_p95_ms"]),
        elapsed_steps=int(state["elapsed_steps"]),
        runbook_phase=int(state["runbook_phase"]),
        escalation_budget=int(state["escalation_budget"]),
        is_resolved=bool(state["is_resolved"]),
        sla_breach_risk=float(state["sla_breach_risk"]),
    )


def _grade(state: dict, max_steps: int) -> dict:
    current_state = _state_from_dict(state)
    score = EvaluationGrader.episode_score(current_state, max_steps=max_steps)
    return {
        "score": score,
        "success": EvaluationGrader.is_success(score),
    }


def grade_easy(state: dict, max_steps: int = 12) -> dict:
    return _grade(state=state, max_steps=max_steps)


def grade_medium(state: dict, max_steps: int = 15) -> dict:
    return _grade(state=state, max_steps=max_steps)


def grade_hard(state: dict, max_steps: int = 18) -> dict:
    return _grade(state=state, max_steps=max_steps)


GRADER_REGISTRY = {
    "easy": grade_easy,
    "medium": grade_medium,
    "hard": grade_hard,
}
