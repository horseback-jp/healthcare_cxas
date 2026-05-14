# Healthcare Support Triage Agent — NHS Demographic Capture

A standalone telephony concierge voice agent built on the Google Customer Engagement Suite (GECX / CXAS) platform. 

Designed to act as the first line of telephony support, contextualizing calls, capturing necessary demographic data, executing age-based escalation routing, and summarizing caller needs while strictly adhering to medical advice guardrails.

## Architecture & Scope

- **Agent**: `healthcare_support_triage_agent` (Single-Agent architecture).
- **Modality**: Configured for Voice / Telephony interactions with streaming audio capabilities.
- **Integration Level**: Standalone demo (no backend data dips or external API integrations required).

### Conversational Flow & Phases
1. **Greeting & Context**: Warm opening to establish if the caller is calling for themselves or on behalf of someone else (sets `is_third_party_caller`).
2. **Demographic Capture**: Dynamic entity extraction of Patient Name, Age, and Postcode (plus Caller Name for third-party paths). Supports multi-entity out-of-order utterances and patient question breakdown for confused callers.
3. **Escalation Check**: Age-based routing logic (`patient_age < 13`) triggering immediate transfer to a human specialist.
4. **Intent Capture**: Prompts for primary symptoms/reasons for call while strictly enforcing guardrails against medical advice or diagnosis.
5. **Handoff**: Empathetic summary of captured demographics and reason for call, transferring to the triage team queue.

---

## Repository Structure

```
jphNhsDemographicCapture/
├── gecx-config.json                   # Project configuration & deployed app ID
├── tdd.md                             # Living Technical Design Document & pass rate history
├── experiment_log.md                  # Historical iteration and experiment tracking
├── cxas_app/                          # Canonical GECX agent definitions
│   └── nhs_demographic_capture/
│       ├── app.json                   # App settings, thresholds, and variable declarations
│       ├── agents/
│       │   └── healthcare_support_triage_agent/
│       │       ├── healthcare_support_triage_agent.json
│       │       ├── instruction.txt    # Structured XML instructions
│       │       ├── before_model_callbacks/
│       │       └── after_model_callbacks/
│       └── tools/
│           ├── set_session_state/     # Internal trigger management tool
│           ├── set_demographics/      # Demographic extraction tool
│           ├── set_reason_for_call/   # Intent capture tool
│           └── transfer_call/         # Deterministic handoff tool
└── evals/                             # Verification and evaluation suites
    ├── goldens/                       # Replay evaluations for deterministic flows
    ├── simulations/                   # LLM-judged open-ended simulation evaluations
    ├── tool_tests/                    # Isolated tool schema tests
    └── callback_tests/                # Pytest callback unit tests
```

---

## Deterministic Callback Patterns

To guarantee high reliability and prevent LLM behavioral drift, critical execution paths are enforced via Python callbacks:

- **Trigger Pattern (`before_model_callback`)**: The LLM identifies intent and sets an internal state flag (`_action_trigger`) via `set_session_state`. The callback intercepts the subsequent turn to execute deterministic tool calls (`transfer_call` and `end_session`).
- **Silence Handling (`before_model_callback`)**: Intercepts telephony inactivity signals to repeat prompts twice before ending the session gracefully.
- **Farewell Prepending (`after_model_callback`)**: Detects silent `end_session` invocations and prepends a professional goodbye message before the call disconnects.

---

## Team Development & CI/CD Workflow

To support collaborative engineering without colliding on the production app, this repository follows a Git-centric CI/CD workflow:

### 1. Local Sandbox Development
When developing a new feature, create a personal sandbox app on GECX by branching the main production app:
```bash
git checkout -b feat/new-routing
cxas branch "projects/ces-demo-emea/locations/us/apps/7dfa445b-21d4-4c61-b0f9-10e6bcfcb389" \
  --new-name "[dev-sandbox]nhsDemographicCapture" \
  --project-id ces-demo-emea --location us
```
Temporarily point `gecx-config.json` to your sandbox app ID, iterate locally, and verify with `cxas lint`.

### 2. Evaluation Runner
Execute local verification against your sandbox app across Goldens, Simulations, and Tool Tests:
```bash
python .agents/skills/cxas-agent-foundry/scripts/run-and-report.py --message "Feature verification" --runs 3
```

### 3. Pull Request & CI/CD
Once verified locally, revert `gecx-config.json` to the production app ID (`7dfa445b-21d4-4c61-b0f9-10e6bcfcb389`) and open a GitHub Pull Request. 

Merging the PR into `main` automatically triggers your CI/CD deployment pipeline (e.g., GitHub Actions) to deploy the canonical code:
```bash
cxas push --app-dir cxas_app/nhs_demographic_capture \
  --to projects/ces-demo-emea/locations/us/apps/7dfa445b-21d4-4c61-b0f9-10e6bcfcb389 \
  --project-id ces-demo-emea --location us
```
