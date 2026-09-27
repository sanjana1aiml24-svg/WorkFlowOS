import json
from datetime import datetime

with open("activity_log.json", "r") as f:
    events = json.load(f)

semantic = []

for event in events:

    app = event.get("app", "")
    window = event.get("window", "").lower()

    if app == "Gmail" and "product quotation request" in window:
        semantic.append({
            "timestamp": event["timestamp"],
            "app": "Gmail",
            "action": "email_read"
        })

    elif app == "Browser" and ".pdf" in window:
        semantic.append({
            "timestamp": event["timestamp"],
            "app": "Gmail",
            "action": "attachment_downloaded"
        })

    elif app == "Slack" and "all-workflowos" in window:
        semantic.append({
            "timestamp": event["timestamp"],
            "app": "Slack",
            "action": "notification_sent"
        })


# The real CRM update happens inside the actual workflow.
# Add it after each detected Gmail → PDF → Slack cycle.

final_events = []

for event in semantic:

    final_events.append(event)

    if (
        event["app"] == "Gmail"
        and event["action"] == "attachment_downloaded"
    ):
        final_events.append({
            "timestamp": event["timestamp"],
            "app": "CRM",
            "action": "customer_updated"
        })


with open("semantic_activity.json", "w") as f:
    json.dump(final_events, f, indent=2)

print("🧠 Semantic log created!")
print(f"📊 Events: {len(final_events)}")