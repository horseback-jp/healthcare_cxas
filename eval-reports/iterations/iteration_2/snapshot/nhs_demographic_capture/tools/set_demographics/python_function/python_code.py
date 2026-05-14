# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
set_demographics — Demographic Capture Tool

PURPOSE:
    Captures demographic data extracted during the conversation, updating session state.
"""


def set_demographics(is_third_party_caller: str = "false",
                     caller_first_name: str = "",
                     caller_last_name: str = "",
                     patient_first_name: str = "",
                     patient_last_name: str = "",
                     patient_age: int = 0,
                     patient_home_postcode: str = "") -> dict:
    """Write captured demographics to session state.

    Args:
        is_third_party_caller: 'true' if calling on behalf of someone else, 'false' otherwise.
        caller_first_name: First name of caller if third party.
        caller_last_name: Last name of caller if third party.
        patient_first_name: First name of patient.
        patient_last_name: Last name of patient.
        patient_age: Age of patient as integer.
        patient_home_postcode: Home postcode of patient.

    Returns:
        dict: Confirmation of captured demographic values.
    """
    # Ensure required parameters are present or being accumulated
    if not patient_first_name and not caller_first_name and patient_age == 0 and not patient_home_postcode:
        return {
            "agent_action": "You must provide at least one demographic field (name, age, or postcode)."
        }

    context.state["is_third_party_caller"] = is_third_party_caller.lower()
    if caller_first_name:
        context.state["caller_first_name"] = caller_first_name
    if caller_last_name:
        context.state["caller_last_name"] = caller_last_name
    if patient_first_name:
        context.state["patient_first_name"] = patient_first_name
    if patient_last_name:
        context.state["patient_last_name"] = patient_last_name
    if patient_age > 0:
        context.state["patient_age"] = str(patient_age)
    if patient_home_postcode:
        context.state["patient_home_postcode"] = patient_home_postcode

    return {
        "status": "success",
        "captured_demographics": {
            "is_third_party_caller": context.state.get("is_third_party_caller", ""),
            "caller_first_name": context.state.get("caller_first_name", ""),
            "caller_last_name": context.state.get("caller_last_name", ""),
            "patient_first_name": context.state.get("patient_first_name", ""),
            "patient_last_name": context.state.get("patient_last_name", ""),
            "patient_age": context.state.get("patient_age", ""),
            "patient_home_postcode": context.state.get("patient_home_postcode", "")
        }
    }
