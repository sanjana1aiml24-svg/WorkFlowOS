import json

STATE_FILE = "automation_state.json"


def activate_automation(workflow):
    state = {
        "active": True,
        "workflow": workflow
    }

    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def automation_is_active():

    try:
        with open(STATE_FILE, "r") as f:
            state = json.load(f)

        return state.get("active", False)

    except FileNotFoundError:
        return False


def get_automation():

    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)

    except FileNotFoundError:
        return {}