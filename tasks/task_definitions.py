TASKS = {
    "easy": {
        "title": "Single Service Outage",
        "everyday_impact": "A common app feature goes down and users cannot complete one key action.",
        "who_benefits": "App users, support teams, and operations engineers.",
        "example_story": "A payment button fails for a subset of users during checkout.",
        "severity": 2,
        "affected_services": 1,
        "error_rate": 0.28,
        "latency_p95_ms": 420,
        "runbook_phase": 0,
        "escalation_budget": 2,
        "max_steps": 12,
        "limits": {
            "min_latency_ms": 80.0,
            "max_runbook_phase": 6,
        },
        "resolution_criteria": {
            "max_error_rate": 0.08,
            "max_latency_p95_ms": 220.0,
            "max_sla_risk": 0.22,
        },
        "dynamics": {
            "passive_risk_increase": 0.015,
            "prioritize_risk_reduction": 0.05,
            "diagnostics_error_reduction": 0.02,
            "runbook_error_reduction": 0.12,
            "runbook_latency_reduction_ms": 85.0,
            "runbook_risk_reduction": 0.10,
            "runbook_early_risk_penalty": 0.04,
            "rollback_error_reduction": 0.17,
            "rollback_latency_reduction_ms": 110.0,
            "rollback_risk_reduction": 0.08,
            "escalation_risk_reduction": 0.03,
            "false_resolve_risk_penalty": 0.06,
        },
    },
    "medium": {
        "title": "Multi-Service Slowdown",
        "everyday_impact": "Users see delays and intermittent failures across multiple app screens.",
        "who_benefits": "Customer-facing teams and reliability engineers.",
        "example_story": "Food delivery tracking and payment both become slow at peak traffic.",
        "severity": 3,
        "affected_services": 3,
        "error_rate": 0.41,
        "latency_p95_ms": 580,
        "runbook_phase": 0,
        "escalation_budget": 2,
        "max_steps": 15,
        "limits": {
            "min_latency_ms": 95.0,
            "max_runbook_phase": 7,
        },
        "resolution_criteria": {
            "max_error_rate": 0.09,
            "max_latency_p95_ms": 260.0,
            "max_sla_risk": 0.25,
        },
        "dynamics": {
            "passive_risk_increase": 0.018,
            "prioritize_risk_reduction": 0.05,
            "diagnostics_error_reduction": 0.022,
            "runbook_error_reduction": 0.115,
            "runbook_latency_reduction_ms": 80.0,
            "runbook_risk_reduction": 0.095,
            "runbook_early_risk_penalty": 0.045,
            "rollback_error_reduction": 0.15,
            "rollback_latency_reduction_ms": 100.0,
            "rollback_risk_reduction": 0.07,
            "escalation_risk_reduction": 0.03,
            "false_resolve_risk_penalty": 0.065,
        },
    },
    "hard": {
        "title": "Cascading Incident",
        "everyday_impact": "A chain of failures creates broad instability and user trust risk.",
        "who_benefits": "Entire platform operations and business stakeholders.",
        "example_story": "A release issue causes login, search, and checkout failures together.",
        "severity": 4,
        "affected_services": 5,
        "error_rate": 0.57,
        "latency_p95_ms": 760,
        "runbook_phase": 0,
        "escalation_budget": 1,
        "max_steps": 18,
        "limits": {
            "min_latency_ms": 110.0,
            "max_runbook_phase": 8,
        },
        "resolution_criteria": {
            "max_error_rate": 0.10,
            "max_latency_p95_ms": 320.0,
            "max_sla_risk": 0.28,
        },
        "dynamics": {
            "passive_risk_increase": 0.022,
            "prioritize_risk_reduction": 0.045,
            "diagnostics_error_reduction": 0.02,
            "runbook_error_reduction": 0.105,
            "runbook_latency_reduction_ms": 70.0,
            "runbook_risk_reduction": 0.09,
            "runbook_early_risk_penalty": 0.05,
            "rollback_error_reduction": 0.14,
            "rollback_latency_reduction_ms": 90.0,
            "rollback_risk_reduction": 0.065,
            "escalation_risk_reduction": 0.025,
            "false_resolve_risk_penalty": 0.07,
        },
    },
}


TASK_GRADERS = {
    "easy": {
        "id": "grader_easy_recovery",
        "function": "tasks.graders.grade_easy",
        "description": "Validates easy recovery criteria and normalized score.",
    },
    "medium": {
        "id": "grader_medium_recovery",
        "function": "tasks.graders.grade_medium",
        "description": "Validates medium recovery criteria and normalized score.",
    },
    "hard": {
        "id": "grader_hard_recovery",
        "function": "tasks.graders.grade_hard",
        "description": "Validates hard recovery criteria and normalized score.",
    },
}

ACTIONS = [
    "prioritize_incident",
    "query_diagnostics",
    "apply_runbook_step",
    "rollback_release",
    "escalate_oncall",
    "mark_resolved",
]


TASK_SUMMARY = {
    "easy": {
        "goal_plain": "Restore one broken feature quickly with minimal escalation.",
        "success_plain": "Users can use the feature again without visible delay.",
    },
    "medium": {
        "goal_plain": "Stabilize multiple connected services while controlling response cost.",
        "success_plain": "Most user flows recover and latency returns close to normal.",
    },
    "hard": {
        "goal_plain": "Stop cascading failures and recover safely under strict action limits.",
        "success_plain": "Critical journeys recover without exhausting escalation budget.",
    },
}


def build_tasks_with_graders() -> list[dict]:
    payload = []
    for task_id, config in TASKS.items():
        payload.append(
            {
                "id": task_id,
                "title": config["title"],
                "difficulty": task_id,
                "target": TASK_SUMMARY[task_id]["goal_plain"],
                "grader": TASK_GRADERS[task_id],
                "score_range": {"min": 0.0, "max": 1.0},
            }
        )
    return payload

