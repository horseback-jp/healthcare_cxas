# Experiment Log

Tracking what was tried, results across all eval types, and failure details.

## Iteration 1 — 2026-05-14
**Change:** Initial baseline

| Eval Type | Pass Rate |
|-----------|-----------|
| Goldens | 0/0 (0%) |
| Tool Tests | 5/5 (100%) |

## Iteration 2 — 2026-05-14
**Change:** Initial baseline

| Eval Type | Pass Rate |
|-----------|-----------|
| Goldens | 0/0 (0%) |
| Tool Tests | 5/5 (100%) |

## Iteration 3 — 2026-05-14
**Change:** Initial baseline

| Eval Type | Pass Rate |
|-----------|-----------|
| Goldens | 0/9 (0%) |
| Tool Tests | 5/5 (100%) |

**Golden failures:**
- `TOOL_MISSING` scenario_1_adult_confused x3: expected set_reason_for_call, got set_reason_for_call. Called: [set_demographics, set_reason_for_cal
- `EXPECTATION_FAIL` scenario_2_adult_efficient x3: "The agent must match the caller's efficient tone." — The user's tone is efficient and direct throug
- `EXPECTATION_FAIL` scenario_3_child_escalation: "The agent must capture both caller and patient demographics " — The agent successfully identified t
- `TEXT_MISMATCH` scenario_3_child_escalation x2: sem_score=2

