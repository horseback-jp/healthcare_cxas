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
set_reason_for_call — Reason for Call Capture Tool

PURPOSE:
    Records the primary reason for call or symptom description in session state.
"""


def set_reason_for_call(reason_for_call: str = "") -> dict:
    """Write captured reason for call to session state.

    Args:
        reason_for_call: Detailed reason for call or symptom description.

    Returns:
        dict: Confirmation of captured reason for call.
    """
    if not reason_for_call:
        return {
            "agent_action": "You must provide a valid reason_for_call description."
        }

    context.state["reason_for_call"] = reason_for_call

    return {
        "status": "success",
        "captured_reason": reason_for_call
    }
