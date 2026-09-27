import subprocess
import time

from event_logger import log_event

CHECK_INTERVAL = 1


def get_active_window():
    try:
        window_id = subprocess.check_output(
            ["xdotool", "getactivewindow"],
            text=True
        ).strip()

        window_name = subprocess.check_output(
            ["xdotool", "getwindowname", window_id],
            text=True
        ).strip()

        return window_name

    except Exception:
        return ""


def identify_app(window):
    text = window.lower()

    if "gmail" in text:
        return "Gmail"

    if "slack" in text:
        return "Slack"

    return "Other"


def gmail_action(window):
    lower = window.lower()

    if "gmail" not in lower:
        return None

    if "inbox" in lower:
        return "email_list_view"

    return "email_read"


def slack_action(window):
    lower = window.lower()

    if "slack" in lower:
        return "channel_opened"

    return None


def main():

    print("=" * 60)
    print("🤖 WorkFlowOS REAL ACTIVITY OBSERVER")
    print("=" * 60)
    print("Watching Gmail + Slack activity...")
    print("Browser PDF/navigation windows are ignored.")
    print("Press Ctrl+C to stop.\n")

    last_window = ""
    last_action = ""

    while True:

        try:

            window = get_active_window()

            if not window:
                time.sleep(CHECK_INTERVAL)
                continue

            app = identify_app(window)

            # Ignore browser pages, terminals, VS Code,
            # PDF viewers, and every other unrelated window.
            if app == "Other":
                last_window = window
                time.sleep(CHECK_INTERVAL)
                continue

            if window != last_window:

                print(f"👀 {app}: {window}")

                action = None

                if app == "Gmail":
                    action = gmail_action(window)

                elif app == "Slack":
                    action = slack_action(window)

                if action:

                    event_key = f"{app}:{action}"

                    if event_key != last_action:

                        log_event(
                            app,
                            action,
                            {
                                "window": window
                            }
                        )

                        last_action = event_key

                last_window = window

            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:

            print("\n🛑 Activity observer stopped.")
            break

        except Exception as e:

            print("⚠️ Observer error:", e)
            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()