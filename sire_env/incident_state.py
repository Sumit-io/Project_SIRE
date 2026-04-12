from dataclasses import asdict, dataclass


@dataclass
class IncidentState:
    """Incident state used by the environment and exposed via state()."""

    severity: int
    affected_services: int
    error_rate: float
    latency_p95_ms: float
    elapsed_steps: int
    runbook_phase: int
    escalation_budget: int
    is_resolved: bool
    sla_breach_risk: float

    def to_dict(self) -> dict:
        return asdict(self)

    def to_vector(self) -> list[float]:
        return [
            float(self.severity),
            float(self.affected_services),
            float(self.error_rate),
            float(self.latency_p95_ms),
            float(self.elapsed_steps),
            float(self.runbook_phase),
            float(self.escalation_budget),
            float(self.sla_breach_risk),
        ]
