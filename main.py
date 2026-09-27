# WorkFlowOS - Workflow Discovery Engine

events = [
    # First occurrence
    {"app": "Gmail", "action": "open_email"},
    {"app": "Gmail", "action": "download_attachment"},
    {"app": "CRM", "action": "open_customer"},
    {"app": "CRM", "action": "update_customer"},
    {"app": "Slack", "action": "send_message"},

    # Second occurrence
    {"app": "Gmail", "action": "open_email"},
    {"app": "Gmail", "action": "download_attachment"},
    {"app": "CRM", "action": "open_customer"},
    {"app": "CRM", "action": "update_customer"},
    {"app": "Slack", "action": "send_message"},

    # Third occurrence
    {"app": "Gmail", "action": "open_email"},
    {"app": "Gmail", "action": "download_attachment"},
    {"app": "CRM", "action": "open_customer"},
    {"app": "CRM", "action": "update_customer"},
    {"app": "Slack", "action": "send_message"}
]


# Extract only the actions
actions = [event["action"] for event in events]

print("Observed actions:")
print(actions)


# The workflow we are looking for
workflow_length = 5

first = actions[0:5]
second = actions[5:10]
third = actions[10:15]


# Check whether all three sequences are identical
if first == second == third:

    print("\n🔍 REPEATED WORKFLOW DETECTED!")

    print("\nWorkflow:")
    print(" → ".join(first))

    print("\nOccurrences: 3")

else:
    print("\nNo repeated workflow detected.")
    # Step 3 - Generate a structured workflow

workflow = {
    "name": "Process Customer Request",

    "trigger": "New customer request received",

    "actions": [
        "Read the customer email",
        "Download the attachment",
        "Find the customer in the CRM",
        "Update the customer record",
        "Notify the relevant team"
    ],

    "condition": "If customer cannot be found, request user intervention"
}


print("\n" + "=" * 50)
print("GENERATED WORKFLOW")
print("=" * 50)

print(f"\nName: {workflow['name']}")
print(f"\nTrigger: {workflow['trigger']}")

print("\nActions:")
for i, action in enumerate(workflow["actions"], start=1):
    print(f"{i}. {action}")

print(f"\nCondition: {workflow['condition']}")