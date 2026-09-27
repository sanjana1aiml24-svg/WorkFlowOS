import json
import os
import time
from collections import Counter
from dotenv import load_dotenv
from google import genai

load_dotenv()

LOG_FILE = "semantic_activity.json"

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

IGNORED_ACTIONS = {
    "email_list_view",
    "channel_opened"
}


# ---------------------------------------------------------
# LOAD EVENTS
# ---------------------------------------------------------

def load_events():
    if not os.path.exists(LOG_FILE):
        return []

    try:
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []


# ---------------------------------------------------------
# NORMALIZE EVENTS
# ---------------------------------------------------------

def normalize_event(event):

    app = event.get("app", "").lower().strip()
    action = event.get("action", "").lower().strip()

    replacements = {
        "open_email": "email_read",
        "read_email": "email_read",
        "email_received": "email_read",
        "send_message": "message_sent",
        "notification_sent": "message_sent"
    }

    action = replacements.get(action, action)

    if action in IGNORED_ACTIONS:
        return None

    # Only consider applications relevant to WorkFlowOS.
    if app not in {
        "gmail",
        "slack",
        "crm"
    }:
        return None

    return f"{app}:{action}"


# ---------------------------------------------------------
# BUILD SEMANTIC SEQUENCE
# ---------------------------------------------------------

def build_sequence(events):

    sequence = []

    for event in events:

        normalized = normalize_event(event)

        if normalized:
            # IMPORTANT:
            # Do NOT remove repeated events.
            #
            # Repetition is exactly what WorkFlowOS
            # needs to detect.
            sequence.append(normalized)

    return sequence


# ---------------------------------------------------------
# FIND REPEATED PATTERNS
# ---------------------------------------------------------

def find_repeated_patterns(events):

    sequence = build_sequence(events)

    if not sequence:
        return None

    # Count meaningful actions.
    counts = Counter(sequence)

    # Ignore actions that are not useful for workflow discovery.
    ignored_for_pattern = {
        "gmail:email_list_view",
        "slack:channel_opened"
    }

    meaningful = [
        action
        for action in sequence
        if action not in ignored_for_pattern
    ]

    if len(meaningful) < 3:
        return None

    # Find actions that occurred at least 3 times.
    repeated = [
        action
        for action, count in counts.items()
        if count >= 3
        and action not in ignored_for_pattern
    ]

    if not repeated:
        return None

    # Preserve the order in which repeated actions first appeared.
    pattern = []

    for action in sequence:

        if action in repeated and action not in pattern:
            pattern.append(action)

    if not pattern:
        return None

    occurrences = min(
        counts[action]
        for action in pattern
    )

    if occurrences < 3:
        return None

    return {
        "sequence": pattern,
        "occurrences": occurrences
    }


# ---------------------------------------------------------
# GEMINI AI INTERPRETATION
# ---------------------------------------------------------

def ask_ai(pattern):

    prompt = f"""
You are the AI workflow discovery engine inside WorkFlowOS.

WorkFlowOS observes real user activity across desktop applications.

A repeated sequence of real user actions was detected:

{json.dumps(pattern, indent=2)}

Understand what the USER is repeatedly doing.

Return ONLY valid JSON.

Use exactly this structure:

{{
    "workflow_name": "short human-readable workflow name",
    "intent": "what the user is trying to accomplish",
    "trigger": "what event should trigger this workflow",
    "steps": [
        "step 1",
        "step 2",
        "step 3"
    ],
    "condition": "when human intervention may be required",
    "confidence": 85
}}

Rules:

1. Do not invent applications that are not present.
2. Convert technical events into understandable user actions.
3. Keep the workflow practical.
4. Confidence must be an integer from 0 to 100.
5. If the sequence contains Gmail email reading and attachment downloading,
   interpret it as an email attachment workflow.
6. If Slack message sending is present, mention notifying Slack.
7. Return JSON only.
"""

    for attempt in range(3):

        try:

            print(
                f"🤖 Asking Gemini to interpret workflow "
                f"(attempt {attempt + 1}/3)..."
            )

            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt
            )

            text = response.text.strip()

            # Remove markdown JSON fences if Gemini adds them.
            if text.startswith("```"):
                text = text.replace("```json", "")
                text = text.replace("```", "")
                text = text.strip()

            result = json.loads(text)

            return result

        except Exception as e:

            print(
                f"⚠️ Gemini attempt {attempt + 1} failed:",
                e
            )

            if attempt < 2:
                print("⏳ Retrying in 3 seconds...")
                time.sleep(3)

    raise RuntimeError(
        "Gemini was unavailable after 3 attempts."
    )


# ---------------------------------------------------------
# DISCOVER WORKFLOW
# ---------------------------------------------------------

def discover():

    events = load_events()

    if not events:
        return None

    repeated = find_repeated_patterns(events)

    if not repeated:
        return None

    try:

        ai_result = ask_ai(repeated)

    except Exception as e:

        print(
            "⚠️ AI interpretation error:",
            e
        )

        return None

    sequence = repeated["sequence"]

    applications = list({
        step.split(":", 1)[0]
        for step in sequence
    })

    return {
        "workflow_name": ai_result.get(
            "workflow_name",
            "AI-Discovered Workflow"
        ),

        "sequence": sequence,

        "occurrences": repeated["occurrences"],

        "confidence": ai_result.get(
            "confidence",
            0
        ),

        "applications": applications,

        "intent": ai_result.get(
            "intent",
            "Repeated digital workflow detected."
        ),

        "trigger": ai_result.get(
            "trigger",
            "Repeated activity detected."
        ),

        "steps": ai_result.get(
            "steps",
            []
        ),

        "condition": ai_result.get(
            "condition",
            "Human intervention may be required."
        )
    }


# ---------------------------------------------------------
# TEST WHEN RUN DIRECTLY
# ---------------------------------------------------------

if __name__ == "__main__":

    print("=" * 55)
    print("🧠 WorkFlowOS Pattern Engine")
    print("=" * 55)

    events = load_events()

    print(f"📊 Raw events: {len(events)}")

    sequence = build_sequence(events)

    print("\n🔎 Semantic sequence:")

    for i, event in enumerate(sequence, 1):
        print(f"{i}. {event}")

    repeated = find_repeated_patterns(events)

    print("\n🔁 Repeated pattern:")

    if repeated:
        print(
            json.dumps(
                repeated,
                indent=2
            )
        )
    else:
        print("None detected.")

    if repeated:

        print("\n🤖 AI workflow interpretation:")

        result = discover()

        print(
            json.dumps(
                result,
                indent=2
            )
        )

    else:

        print(
            "\n⏳ Not enough repeated activity yet."
        )
