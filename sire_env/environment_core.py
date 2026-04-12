from copy import deepcopy

from sire_env.evaluation_grader import EvaluationGrader
from sire_env.incident_state import IncidentState
from tasks.task_definitions import ACTIONS, TASKS


def _clip(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


class SireEnvironment:
    """OpenEnv-style core with reset(), step(), and state() semantics."""

    def __init__(self) -> None:
        self.task_id = "easy"
        self.task_config = TASKS[self.task_id]
        self.max_steps = self.task_config["max_steps"]
        self.current_state = self._build_state(self.task_id)

    def _build_state(self, task_id: str) -> IncidentState:
        cfg = TASKS[task_id]
        return IncidentState(
            severity=cfg["severity"],
            affected_services=cfg["affected_services"],
            error_rate=cfg["error_rate"],
            latency_p95_ms=cfg["latency_p95_ms"],
            elapsed_steps=0,
            runbook_phase=cfg["runbook_phase"],
            escalation_budget=cfg["escalation_budget"],
            is_resolved=False,
            sla_breach_risk=_clip(0.22 * cfg["severity"], 0.0, 1.0),
        )

    def available_actions(self) -> list[str]:
        return ACTIONS

    def reset(self, task_id: str = "easy") -> dict:
        self.task_id = task_id if task_id in TASKS else "easy"
        self.task_config = TASKS[self.task_id]
        self.max_steps = self.task_config["max_steps"]
        self.current_state = self._build_state(self.task_id)
        return {
            "task_id": self.task_id,
            "state": self.current_state.to_dict(),
            "available_actions": self.available_actions(),
        }

    def state(self) -> dict:
        return {
            "task_id": self.task_id,
            "state": self.current_state.to_dict(),
            "available_actions": self.available_actions(),
            "max_steps": self.max_steps,
        }

    def step(self, action: str) -> dict:
        if self.current_state.is_resolved or self.current_state.elapsed_steps >= self.max_steps:
            score = EvaluationGrader.episode_score(self.current_state, self.max_steps)
            return {
                "action": "noop",
                "reward": 0.0,
                "done": True,
                "state": self.current_state.to_dict(),
                "info": {
                    "task_id": self.task_id,
                    "score": score,
                    "success": EvaluationGrader.is_success(score),
                    "already_terminal": True,
                },
            }

        if action not in ACTIONS:
            return {
                "error": f"invalid action: {action}",
                "available_actions": ACTIONS,
                "done": False,
                "state": self.current_state.to_dict(),
            }

        previous_state = deepcopy(self.current_state)
        self._apply_action(action)
        self.current_state.elapsed_steps += 1
        self._enforce_state_bounds()

        done = self.current_state.is_resolved or self.current_state.elapsed_steps >= self.max_steps
        reward = EvaluationGrader.transition_reward(previous_state, self.current_state, action)
        score = EvaluationGrader.episode_score(self.current_state, self.max_steps) if done else None

        return {
            "action": action,
            "reward": reward,
            "done": done,
            "state": self.current_state.to_dict(),
            "info": {
                "task_id": self.task_id,
                "score": score,
                "success": EvaluationGrader.is_success(score) if score is not None else None,
            },
        }

    def _is_resolution_valid(self) -> bool:
        criteria = self.task_config["resolution_criteria"]
        state = self.current_state
        return (
            state.error_rate <= criteria["max_error_rate"]
            and state.latency_p95_ms <= criteria["max_latency_p95_ms"]
            and state.sla_breach_risk <= criteria["max_sla_risk"]
        )

    def _enforce_state_bounds(self) -> None:
        limits = self.task_config["limits"]
        state = self.current_state
        state.error_rate = _clip(state.error_rate, 0.0, 1.0)
        state.sla_breach_risk = _clip(state.sla_breach_risk, 0.0, 1.0)
        state.latency_p95_ms = max(limits["min_latency_ms"], state.latency_p95_ms)
        state.runbook_phase = int(_clip(float(state.runbook_phase), 0.0, float(limits["max_runbook_phase"])))

    def _apply_action(self, action: str) -> None:
        state = self.current_state
        limits = self.task_config["limits"]
        dynamics = self.task_config["dynamics"]

        if action == "prioritize_incident":
            state.sla_breach_risk = _clip(state.sla_breach_risk - dynamics["prioritize_risk_reduction"], 0.0, 1.0)
            state.runbook_phase = min(state.runbook_phase + 1, limits["max_runbook_phase"])

        elif action == "query_diagnostics":
            state.runbook_phase = min(state.runbook_phase + 1, limits["max_runbook_phase"])
            state.error_rate = _clip(state.error_rate - dynamics["diagnostics_error_reduction"], 0.0, 1.0)

        elif action == "apply_runbook_step":
            if state.runbook_phase > 0:
                state.error_rate = _clip(state.error_rate - dynamics["runbook_error_reduction"], 0.0, 1.0)
                state.latency_p95_ms = max(limits["min_latency_ms"], state.latency_p95_ms - dynamics["runbook_latency_reduction_ms"])
                state.sla_breach_risk = _clip(state.sla_breach_risk - dynamics["runbook_risk_reduction"], 0.0, 1.0)
            else:
                state.sla_breach_risk = _clip(state.sla_breach_risk + dynamics["runbook_early_risk_penalty"], 0.0, 1.0)

        elif action == "rollback_release":
            state.error_rate = _clip(state.error_rate - dynamics["rollback_error_reduction"], 0.0, 1.0)
            state.latency_p95_ms = max(limits["min_latency_ms"], state.latency_p95_ms - dynamics["rollback_latency_reduction_ms"])
            state.sla_breach_risk = _clip(state.sla_breach_risk - dynamics["rollback_risk_reduction"], 0.0, 1.0)

        elif action == "escalate_oncall":
            state.escalation_budget -= 1
            state.sla_breach_risk = _clip(state.sla_breach_risk - dynamics["escalation_risk_reduction"], 0.0, 1.0)

        elif action == "mark_resolved":
            if self._is_resolution_valid():
                state.is_resolved = True
            else:
                state.sla_breach_risk = _clip(state.sla_breach_risk + dynamics["false_resolve_risk_penalty"], 0.0, 1.0)

        # Passive degradation if not yet resolved.
        if not state.is_resolved:
            state.sla_breach_risk = _clip(state.sla_breach_risk + dynamics["passive_risk_increase"], 0.0, 1.0)
