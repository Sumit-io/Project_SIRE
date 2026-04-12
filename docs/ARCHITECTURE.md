# Architecture

## High-Level Components
1. Environment Core: manages state transitions, terminal logic, and action effects.
2. Evaluation Grader: computes transition rewards and final episode score.
3. Baseline Policy: selects actions from state vectors.
4. API Layer: exposes environment via FastAPI endpoints.
5. Demo Frontend: provides plain-language, non-technical visualization.
6. Inference Runner: executes end-to-end episodes with strict tagged logs.

## Data Flow
1. Client resets task with `POST /reset`.
2. Environment returns initial state and available actions.
3. Client submits action or policy-driven step with `POST /step`.
4. Environment applies dynamics and returns reward, done, and updated state.
5. Grader computes score at terminal step.
6. UI and logs display episode progress and final outcome.

## Key Files
1. `sire_env/environment_core.py`
2. `sire_env/evaluation_grader.py`
3. `sire_env/baseline_policy.py`
4. `app.py`
5. `inference.py`
6. `tasks/task_definitions.py`
7. `frontend/index.html`

## Design Principles
1. Compliance-first OpenEnv style interactions.
2. Deterministic mode for reliable demos.
3. Strict output tags for evaluator compatibility.
4. Config-driven task difficulty and dynamics.
