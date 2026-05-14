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
before_model_callback — Healthcare Support Triage Agent

PURPOSE:
    Implements the TRIGGER PATTERN for deterministic tool calls and silence handling.
"""

import re
from typing import Iterator, Optional


def is_user_inactive(contents: list) -> bool:
    """Check if the latest user message is a 'no activity' silence signal."""
    silence_pattern = (
        r"<context>no user activity detected for \d+ seconds\.</context>"
    )
    return len(contents) > 1 and any(
        re.search(silence_pattern, p.text, re.IGNORECASE)
        for p in contents[-1].parts
        if p.text
    )


def get_reversed_agent_messages(contents: list) -> Iterator[str]:
    """Yield agent messages from most recent to oldest."""
    for content in reversed(contents):
        texts = []
        for part in content.parts:
            if content.role == "model" and part.text is not None:
                texts.append(part.text)
        if texts:
            yield "".join(texts)


ESCALATION_MAP = {
    "transfer_specialist": {
        "text": "Thank you. Since you are calling about a child under 13, I am going to transfer you to a human specialist who can assist you immediately. Please hold the line.",
        "payload": {
            "transfer_destination": "specialist",
            "summary": "Child patient under 13",
        },
    },
    "transfer_triage": {
        "text": "I have noted down all your details and the reason for your call. I am now going to transfer you to our triage team who can speak with you further about this. Please hold the line.",
        "payload": {
            "transfer_destination": "triage",
            "summary": "Transferring to triage team",
        },
    },
}


def before_model_callback(callback_context: CallbackContext, llm_request: LlmRequest) -> Optional[LlmResponse]:
    state = callback_context.state

    # Session start fixed greeting
    for part in callback_context.get_last_user_input():
        if part.text == "<event>session start</event>":
            greeting = (
                "Hello, thank you for calling healthcare support. "
                "To make sure I help you correctly, are you calling for yourself today, "
                "or on behalf of someone else?"
            )
            return LlmResponse.from_parts(parts=[
                Part.from_text(text=greeting),
            ])

    # Silence handling
    try:
        if is_user_inactive(llm_request.contents):
            no_input_counter = int(state.get("no_input_counter", 0)) + 1
            state["no_input_counter"] = str(no_input_counter)

            if no_input_counter < 3:
                reversed_msgs = get_reversed_agent_messages(llm_request.contents)
                if no_input_counter == 1:
                    last_msg = next(reversed_msgs, "Are you calling for yourself or someone else?")
                    return LlmResponse.from_parts(parts=[
                        Part.from_text(text=f"Sorry, I didn't hear anything. {last_msg}")
                    ])
                else:
                    next(reversed_msgs, None)
                    original_msg = next(reversed_msgs, "Are you calling for yourself or someone else?")
                    return LlmResponse.from_parts(parts=[
                        Part.from_text(text=f"I still can't hear you. {original_msg}")
                    ])
            else:
                return LlmResponse.from_parts(parts=[
                    Part.from_text(
                        text="I'm sorry, but I'm unable to hear you. "
                             "Please try calling again later. Goodbye."
                    ),
                    Part.from_function_call(
                        name="end_session",
                        args={"session_escalated": False, "reason": "no_input_limit"},
                    ),
                ])
        else:
            state["no_input_counter"] = "0"
    except Exception as e:
        print(f"Error in silence handling: {e}")

    trigger_value = state.get("_action_trigger", "")
    if trigger_value:
        state["_action_trigger"] = ""

    if not trigger_value:
        return None

    escalation = ESCALATION_MAP.get(trigger_value)
    if not escalation:
        return None

    return LlmResponse.from_parts(parts=[
        Part.from_text(text=escalation["text"]),
        Part.from_function_call(
            name="transfer_call",
            args=escalation["payload"],
        ),
        Part.from_function_call(
            name="end_session",
            args={"session_escalated": True},
        ),
    ])
