def understand_workflow(sequence):

    normalized = [
        step.lower()
        for step in sequence
    ]

    apps = [
        step.split(":", 1)[0]
        for step in normalized
        if ":" in step
    ]

    actions = [
        step.split(":", 1)[1]
        for step in normalized
        if ":" in step
    ]


    # Gmail + CRM + Slack
    if (
        "gmail" in apps
        and "crm" in apps
        and "slack" in apps
    ):

        return {
            "name":
                "Process Customer Request",

            "intent":
                "Process incoming customer requests "
                "and update the relevant team.",

            "trigger":
                "New customer request received",

            "steps": [
                "Read customer email",
                "Process customer request",
                "Update CRM record",
                "Notify team in Slack"
            ],

            "condition":
                "If the customer cannot be found, "
                "request user intervention"
        }


    # Gmail + Slack
    if (
        "gmail" in apps
        and "slack" in apps
    ):

        return {
            "name":
                "Email Notification Workflow",

            "intent":
                "Process an email and notify "
                "the relevant team automatically.",

            "trigger":
                "New email activity detected",

            "steps": [
                "Process email",
                "Send Slack notification"
            ],

            "condition":
                "Ask the user for intervention "
                "if processing fails"
        }


    # CRM + Slack
    if (
        "crm" in apps
        and "slack" in apps
    ):

        return {
            "name":
                "CRM Update & Team Notification",

            "intent":
                "Update a customer record and "
                "notify the relevant team.",

            "trigger":
                "CRM customer update detected",

            "steps": [
                "Update CRM customer record",
                "Send Slack notification"
            ],

            "condition":
                "Request user intervention "
                "if the CRM update fails"
        }


    # Gmail only
    if "gmail" in apps:

        return {
            "name":
                "Email Processing Workflow",

            "intent":
                "Automate a repeated email "
                "processing activity.",

            "trigger":
                "Repeated Gmail activity detected",

            "steps": [
                action.replace(
                    "_",
                    " "
                ).title()
                for action in actions
            ],

            "condition":
                "Request user intervention "
                "if execution fails"
        }


    # Slack only
    if "slack" in apps:

        return {
            "name":
                "Slack Communication Workflow",

            "intent":
                "Automate a repeated Slack "
                "communication activity.",

            "trigger":
                "Repeated Slack activity detected",

            "steps": [
                action.replace(
                    "_",
                    " "
                ).title()
                for action in actions
            ],

            "condition":
                "Request user intervention "
                "if execution fails"
        }


    # Generic AI-discovered workflow
    readable_steps = []

    for step in sequence:

        if ":" in step:

            app, action = step.split(
                ":",
                1
            )

            readable_steps.append(
                f"{app.title()}: "
                f"{action.replace('_', ' ').title()}"
            )

        else:

            readable_steps.append(
                step
            )


    return {
        "name":
            "AI-Discovered Repetitive Workflow",

        "intent":
            "Automate a repeated sequence "
            "of user actions.",

        "trigger":
            "Repeated activity detected",

        "steps":
            readable_steps,

        "condition":
            "Request user intervention "
            "if execution fails"
    }