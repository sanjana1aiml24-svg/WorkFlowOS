import time
import json
import os
import subprocess

from pattern_engine import discover

STATE_FILE = "pattern_suggestion.json"


def notify(result):

    message = (
        "Repeated workflow detected!\n\n"
        f"{result['workflow_name']}\n"
        f"Occurrences: {result['occurrences']}\n"
        f"Confidence: {result['confidence']}%\n\n"
        "Open WorkFlowOS to review and automate."
    )

    try:
        subprocess.run([
            "notify-send",
            "🤖 WorkFlowOS AI",
            message
        ])
    except Exception:
        pass


def save_suggestion(result):

    with open(
        STATE_FILE,
        "w"
    ) as f:

        json.dump(
            result,
            f,
            indent=2
        )


def main():

    print("=" * 55)
    print("🤖 WorkFlowOS AI PATTERN WATCHER")
    print("=" * 55)
    print("Watching semantic activity...")
    print("Checking for repeated workflows every 5 seconds.")
    print("Press Ctrl+C to stop.\n")

    last_signature = None

    while True:

        try:

            result = discover()

            if result:

                signature = (
                    tuple(result["sequence"]),
                    result["occurrences"]
                )

                if signature != last_signature:

                    print("\n🔔 AI SUGGESTION")
                    print(
                        "Workflow:",
                        result["workflow_name"]
                    )
                    print(
                        "Occurrences:",
                        result["occurrences"]
                    )
                    print(
                        "Confidence:",
                        f"{result['confidence']}%"
                    )

                    save_suggestion(result)
                    notify(result)

                    last_signature = signature

            time.sleep(5)

        except KeyboardInterrupt:

            print(
                "\n🛑 Pattern watcher stopped."
            )
            break

        except Exception as e:

            print(
                "⚠️ Watcher error:",
                e
            )

            time.sleep(5)


if __name__ == "__main__":
    main()