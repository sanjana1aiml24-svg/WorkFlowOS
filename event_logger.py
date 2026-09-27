import json
import os
import uuid
from datetime import datetime


LOG_FILE = "semantic_activity.json"
RUN_FILE = "current_run.json"


def start_run():

    run_id = str(uuid.uuid4())

    run = {
        "run_id": run_id,
        "started_at": datetime.now().isoformat()
    }

    with open(RUN_FILE, "w") as f:
        json.dump(run, f, indent=2)

    return run_id


def get_current_run():

    if not os.path.exists(RUN_FILE):
        return start_run()

    try:
        with open(RUN_FILE, "r") as f:
            run = json.load(f)

        return run["run_id"]

    except Exception:
        return start_run()


def log_event(app, action, details=None):

    try:
        with open(LOG_FILE, "r") as f:
            events = json.load(f)

    except (FileNotFoundError, json.JSONDecodeError):
        events = []

    event = {
        "timestamp":
            datetime.now().isoformat(),

        "run_id":
            get_current_run(),

        "app":
            app,

        "action":
            action,

        "details":
            details or {}
    }

    events.append(event)

    with open(LOG_FILE, "w") as f:
        json.dump(events, f, indent=2)

    print(
        f"🧠 EVENT: {app}:{action}"
    )


if __name__ == "__main__":

    run_id = start_run()

    print(
        "WorkFlowOS Semantic Event Logger"
    )

    print(
        "Run ID:",
        run_id
    )

    print(
        "Ready."
    )