import streamlit as st
import sqlite3
import json
import datetime
import os

from dotenv import load_dotenv
from automation_state import activate_automation

load_dotenv()

DB_NAME = "workflowos_crm.db"
SUGGESTION_FILE = "pattern_suggestion.json"
EXECUTION_FILE = "execution_log.json"
STATE_FILE = "automation_state.json"


st.set_page_config(
    page_title="WorkFlowOS",
    page_icon="🤖",
    layout="wide"
)


def load_json(filename, default):

    if not os.path.exists(filename):
        return default

    try:
        with open(filename, "r") as file:
            return json.load(file)
    except Exception:
        return default


def load_suggestion():
    return load_json(
        SUGGESTION_FILE,
        None
    )


def load_automation_state():
    return load_json(
        STATE_FILE,
        {}
    )


def show_crm():

    connection = sqlite3.connect(DB_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            request TEXT,
            attachment TEXT,
            status TEXT
        )
    """)

    cursor.execute("""
        SELECT id, name, email, request, attachment, status
        FROM customers
    """)

    records = cursor.fetchall()

    connection.close()

    return records


suggestion = load_suggestion()


st.title("🤖 WorkFlowOS")

st.subheader(
    "AI-Powered OS-Level Workflow Automation"
)

st.write(
    "Observe → Understand → Detect → Generate → Approve → Automate"
)


st.markdown("## 🧠 AI Workflow Discovery")


if suggestion:

    workflow_name = suggestion.get(
        "workflow_name",
        "AI-Discovered Workflow"
    )

    sequence = suggestion.get(
        "sequence",
        []
    )

    occurrences = suggestion.get(
        "occurrences",
        0
    )

    confidence = suggestion.get(
        "confidence",
        0
    )

    applications = suggestion.get(
        "applications",
        []
    )

    intent = suggestion.get(
        "intent",
        "Automate a repeated digital workflow."
    )

    trigger = suggestion.get(
        "trigger",
        "Repeated activity detected."
    )

    steps = suggestion.get(
        "steps",
        []
    )

    condition = suggestion.get(
        "condition",
        "Request user intervention if execution fails."
    )


    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Occurrences",
            occurrences
        )

    with col2:
        st.metric(
            "Applications",
            len(applications)
        )

    with col3:
        st.metric(
            "AI Confidence",
            f"{confidence}%"
        )


    st.success(
        "🔔 Repetitive workflow detected by WorkFlowOS AI"
    )


    st.markdown("### 🔍 Observed Activity")

    for step in sequence:

        if ":" in step:

            app, action = step.split(
                ":",
                1
            )

            st.write(
                f"**{app.title()}** → "
                f"{action.replace('_', ' ').title()}"
            )

        else:

            st.write(
                f"→ {step}"
            )


    st.markdown("### 🧠 AI Interpretation")

    st.write(
        "**Workflow:**",
        workflow_name
    )

    st.write(
        "**Intent:**",
        intent
    )

    st.write(
        "**Trigger:**",
        trigger
    )


    st.markdown("### ⚙️ Generated Workflow")

    if steps:

        for index, step in enumerate(
            steps,
            1
        ):

            st.write(
                f"**{index}.** {step}"
            )

    else:

        for index, step in enumerate(
            sequence,
            1
        ):

            st.write(
                f"**{index}.** "
                f"{step.replace('_', ' ').title()}"
            )


    st.warning(
        "Condition: " + condition
    )


    st.markdown("## 🙋 User Approval")

    st.write(
        "WorkFlowOS requires user approval "
        "before activating automation."
    )


    col1, col2 = st.columns(2)


    with col1:

        if st.button(
            "✅ Approve & Automate",
            use_container_width=True
        ):

            workflow = {
                "name": workflow_name,
                "intent": intent,
                "trigger": trigger,
                "steps": steps,
                "condition": condition,
                "observed_sequence": sequence,
                "ai_confidence": confidence
            }

            activate_automation(
                workflow
            )

            execution = {
                "workflow": workflow_name,
                "status": "Automation Activated",
                "timestamp": str(
                    datetime.datetime.now()
                ),
                "ai_confidence": confidence,
                "occurrences": occurrences,
                "observed_sequence": sequence,
                "steps": steps
            }

            with open(
                EXECUTION_FILE,
                "w"
            ) as file:

                json.dump(
                    execution,
                    file,
                    indent=4
                )

            st.success(
                "🤖 Automation activated successfully!"
            )

            st.write(
                "👀 WorkFlowOS is now monitoring "
                "for matching activity."
            )


    with col2:

        if st.button(
            "❌ Reject",
            use_container_width=True
        ):

            st.warning(
                "Workflow rejected by user."
            )


else:

    st.info(
        "👀 WorkFlowOS is observing activity. "
        "A workflow suggestion will appear "
        "when a repeated pattern is detected."
    )


st.markdown("## 🤖 Automation Status")


automation_state = load_automation_state()


if automation_state.get("active"):

    st.success(
        "🟢 Automation Active"
    )

    active_workflow = automation_state.get(
        "workflow",
        {}
    )

    if isinstance(
        active_workflow,
        dict
    ):

        st.write(
            "**Active workflow:**",
            active_workflow.get(
                "name",
                "Workflow"
            )
        )

    st.write(
        "WorkFlowOS is ready to process "
        "matching customer requests."
    )

else:

    st.info(
        "⚪ Automation Inactive"
    )


st.markdown("## 🗄️ CRM Records")


records = show_crm()


if records:

    for record in records:

        st.write({
            "ID": record[0],
            "Customer": record[1],
            "Email": record[2],
            "Request": record[3],
            "Attachment": record[4],
            "Status": record[5]
        })

else:

    st.info(
        "No CRM records yet."
    )


st.divider()

st.caption(
    "WorkFlowOS — AI-powered workflow discovery and automation"
)