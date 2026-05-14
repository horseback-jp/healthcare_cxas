# Technical Design Document (TDD) - NHS Demographic Capture Agent

> This is a **living document** -- update it whenever requirements, agent behavior, or evals change.

## Agent Design

### Architecture
- **Single Agent:** `healthcare_support_triage_agent` (Persona: Clara). Acts as the first line of telephony support concierge.
- **Scope:** Greeting, context establishment (self vs third party), dynamic demographic capture (supports out-of-order entity extraction), age-based escalation routing (`patient_age < 13`), reason for call capture (with strict medical guardrails), and handoff summary.

### Tools
| Tool Name | Type | Purpose |
|-----------|------|---------|
| `set_session_state` | Python function | Generic state writing tool for internal flags / triggers |
| `set_demographics` | Python function | Captures patient name, age, postcode, and optional caller name |
| `set_reason_for_call` | Python function | Captures the caller's intent and reason for call |
| `transfer_call` | Python function | Initiates transfer to triage team or human specialist |

### Routing Logic
- **Phase 1: Greeting & Context:** Determine if calling for self or on behalf of someone else (sets `is_third_party_caller`).
- **Phase 2: Demographic Capture:** Dynamic extraction of Name, Age, Postcode. Supports multi-entity utterances and breaks down questions if caller is confused.
- **Phase 3: Escalation Check:** If `patient_age < 13`, immediately inform caller and route to human specialist.
- **Phase 4: Intent Capture:** If `patient_age >= 13`, prompt for reason for call. Clarify vague statements but strictly enforce guardrails against medical diagnosis/advice.
- **Phase 5: Handoff:** Summarize captured demographics and reason, inform caller of transfer to triage queue, and close interaction.

### Variables
| Variable | Source | Notes |
|----------|--------|-------|
| `is_third_party_caller` | State variable | Boolean flag (stored as string in state) |
| `caller_first_name` | State variable | String |
| `caller_last_name` | State variable | String |
| `patient_first_name` | State variable | String |
| `patient_last_name` | State variable | String |
| `patient_age` | State variable | Integer (stored as string in state) |
| `patient_home_postcode` | State variable | String |
| `reason_for_call` | State variable | String |
| `_action_trigger` | Internal trigger | Set by LLM to invoke deterministic transfer callbacks |

### Callbacks
| Callback | Agent | Purpose |
|----------|-------|---------|
| `before_model` | `healthcare_support_triage_agent` | Intercepts `_action_trigger` to execute deterministic transfer tool calls |
| `after_model` | `healthcare_support_triage_agent` | Ensures agent speaks transfer/farewell text before ending session |

---

## Eval Design

### Coverage Map
| Requirement | Eval Type | Rationale | Priority | Severity | Tags |
|-------------|-----------|-----------|----------|----------|------|
| Confirmed Adult Demographics | Golden | Deterministic flow, empathetic step-by-step extraction | P0 | NO-GO | `demographics, adult-self, scenario-1` |
| Abrupt Adult Extraction | Golden | Deterministic out-of-order extraction, efficient handling | P0 | NO-GO | `demographics, efficient, scenario-2` |
| Child Escalation (< 13) | Golden | Deterministic trigger pattern upon age detection | P0 | NO-GO | `escalation, child-third-party, scenario-3` |
| Guardrail & Vague Intent | Sim | Verifies clarification of vague symptoms without medical advice | P1 | HIGH | `guardrails, intent-capture` |

### Golden vs Sim Decision
- **Use goldens** for deterministic demographic capture, structured routing, and age-based escalation triggers.
- **Use sims** for evaluating natural language clarification of vague symptoms and verifying adherence to medical advice guardrails.

### Test Data (Customer Profiles)
| Profile | Scenario | Description |
|---------|----------|-------------|
| Sarah Jenkins | Scenario 1 | Adult female, 62, SW1A 1AA, calling for self, headache |
| Mark Davies | Scenario 2 | Adult male, 28, M1 1AE, calling for self, knee injury |
| David Smith | Scenario 3 | Calling for son Leo Smith, 10, B1 2QA, unwell |

---

## Build Steps

1. Create app + agent with XML instructions (`healthcare_support_triage_agent`)
2. Create tools + tool configurations (`set_demographics`, `set_reason_for_call`, `transfer_call`)
3. Define variables in `app.json`
4. Implement callbacks (`before_model`, `after_model`)
5. Write golden YAML files (`scenario_1_adult_confused.yaml`, `scenario_2_adult_efficient.yaml`, `scenario_3_child_escalation.yaml`)
6. Write simulation YAML entries
7. Write tool test YAML files
8. Write callback test files
9. Run initial eval suite
10. Iterate and hill-climb

---

## Pass Rate History

| Date | Goldens | Sims | Tool Tests | Callback Tests | Notes |
|------|---------|------|------------|----------------|-------|
| 2026-05-14 | 0/9 (0%) | 0/0 | 5/5 (100%) | 0/0 | Initial baseline run |

---

## Known Issues
- Initial golden expectations require tuning for LLM judge strictness

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2026-05-14 | Introduced agent persona name Clara | Antigravity |
| 2026-05-14 | Initial baseline completed | Antigravity |
