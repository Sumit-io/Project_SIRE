from sire_env.incident_state import IncidentState


def _clip(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


class EvaluationGrader:
    """Grades transitions and final episode outcome in a 0.0 to 1.0 range."""

    @staticmethod
    def transition_reward(previous_state: IncidentState, next_state: IncidentState, action: str) -> float:
        if previous_state.is_resolved:
            return 0.0

        action_penalties = {
            "escalate_oncall": -0.03,
            "rollback_release": -0.02,
        }

        reward = 0.0

        if next_state.error_rate < previous_state.error_rate:
            reward += 0.14
        if next_state.latency_p95_ms < previous_state.latency_p95_ms:
            reward += 0.12
        if next_state.sla_breach_risk < previous_state.sla_breach_risk:
            reward += 0.10

        reward += action_penalties.get(action, 0.0)

        if next_state.escalation_budget < 0:
            reward -= 0.25

        if next_state.is_resolved:
            reward += 0.45

        # A small time penalty pushes the policy toward faster resolution.
        reward -= 0.01
        return _clip(reward, -1.0, 1.0)

    @staticmethod
    def episode_score(state: IncidentState, max_steps: int) -> float:
        time_factor = 1.0 - (state.elapsed_steps / max_steps)
        health_factor = 1.0 - (0.65 * state.error_rate + 0.35 * state.sla_breach_risk)
        escalation_factor = 1.0 if state.escalation_budget >= 0 else 0.7
        resolved_bonus = 1.0 if state.is_resolved else 0.45

        raw = (0.35 * time_factor) + (0.35 * health_factor) + (0.15 * escalation_factor) + (0.15 * resolved_bonus)
        return _clip(raw, 0.0, 1.0)

    @staticmethod
    def is_success(score: float) -> bool:
        return score >= 0.70
