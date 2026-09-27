import json
from collections import Counter

LOG_FILE = "semantic_activity.json"

with open(LOG_FILE, "r") as f:
    events = json.load(f)

activities = [
    f"{event['app']}:{event['action']}"
    for event in events
]

print("🤖 WorkFlowOS AI Pattern Detection Engine\n")
print(f"📊 Semantic events loaded: {len(activities)}\n")

print("👀 Observed Workflow:\n")

for activity in activities:
    print(f" → {activity}")

print("\n🔍 Discovering repeated workflows...\n")


# Create sequences
sequences = []

for length in range(2, min(5, len(activities)) + 1):
    for i in range(len(activities) - length + 1):
        sequences.append(tuple(activities[i:i + length]))


counts = Counter(sequences)

repeated = [
    (sequence, count)
    for sequence, count in counts.items()
    if count >= 2
]


if repeated:

    repeated.sort(
        key=lambda x: (len(x[0]), x[1]),
        reverse=True
    )

    sequence, count = repeated[0]

    print("🚨 REPEATED WORKFLOW DETECTED!\n")
    print(f"Occurrences: {count}\n")

    print("🧠 Workflow:")

    for step in sequence:
        print(f"  → {step}")

    confidence = min(95, 60 + (count * 10))

    print(f"\n📈 Pattern confidence: {confidence}%")

    print("\n🤖 WorkFlowOS Recommendation")
    print("This workflow appears repetitive.")
    print("Automation can be generated.")

    print("\n⚙️ Candidate workflow identified!")

else:

    print("ℹ️ No repeated workflow detected yet.")
    print("The workflow needs to occur more than once.")