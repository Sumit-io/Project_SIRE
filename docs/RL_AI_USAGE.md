# RL and AI Usage

## Where RL Is Used
SIRE follows the standard RL interaction pattern:
1. `reset()` starts an episode.
2. `step(action)` advances environment dynamics.
3. Reward is emitted each step.
4. Episode ends on success or max steps.
5. Final score determines success threshold.

## State, Action, Reward
1. State: severity, affected services, error rate, latency, risk, runbook phase, budget, elapsed steps.
2. Actions: prioritize, diagnostics, runbook step, rollback, escalate, mark resolved.
3. Reward: positive for improving error/latency/risk, penalties for costly or incorrect actions.

## Is LLM Required?
No. LLM interaction is optional.
1. Inference supports a small optional reflection call.
2. If token is absent, execution falls back automatically and continues.
3. Core simulation and scoring work without any API key.

## Is PyTorch Used?
Yes.
1. Baseline policy model is implemented with `torch.nn` layers.
2. Policy loading and tensor-based inference are present in `sire_env/baseline_policy.py`.
3. Deterministic mode currently uses rule-guided policy for stable judge demos.

## Practical Positioning for Judges
1. This is a practical RL-style decision simulator.
2. It includes optional LLM integration, not a dependency.
3. PyTorch is actively used in the policy module.
