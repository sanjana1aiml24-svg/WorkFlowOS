import os
import time
import requests

from dotenv import load_dotenv
from event_logger import log_event


load_dotenv()

BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")

# Verified WorkFlowOS channel
CHANNEL_ID = "C0C4H3PCRGV"
CHANNEL_NAME = "all-workflowos"

CHECK_INTERVAL = 5

HEADERS = {
    "Authorization": f"Bearer {BOT_TOKEN}"
}


def get_messages():

    response = requests.get(
        "https://slack.com/api/conversations.history",
        headers=HEADERS,
        params={
            "channel": CHANNEL_ID,
            "limit": 50
        }
    )

    data = response.json()

    if not data.get("ok"):
        print(
            "⚠️ Slack API error:",
            data.get("error")
        )
        return []

    return data.get(
        "messages",
        []
    )


def main():

    print("=" * 60)
    print("🧠 WorkFlowOS REAL SLACK ACTIVITY COLLECTOR")
    print("=" * 60)
    print(
        f"Monitoring #{CHANNEL_NAME}..."
    )
    print("Press Ctrl+C to stop.\n")

    if not BOT_TOKEN:

        print(
            "❌ SLACK_BOT_TOKEN is missing."
        )
        return

    initial_messages = get_messages()

    seen = set()

    for message in initial_messages:

        if message.get("ts"):
            seen.add(
                message["ts"]
            )

    print(
        f"✅ Connected to #{CHANNEL_NAME}"
    )

    print(
        f"👀 Existing messages ignored: {len(seen)}"
    )

    print(
        "🔄 Waiting for new Slack activity...\n"
    )

    while True:

        try:

            messages = get_messages()

            for message in reversed(messages):

                timestamp = message.get(
                    "ts"
                )

                if not timestamp:
                    continue

                if timestamp in seen:
                    continue

                seen.add(timestamp)

                # Ignore Slack system events
                if message.get("subtype") in [
                    "channel_join",
                    "bot_add",
                    "channel_topic",
                    "channel_purpose"
                ]:
                    continue

                user = message.get(
                    "user",
                    message.get(
                        "bot_id",
                        "unknown"
                    )
                )

                text = message.get(
                    "text",
                    ""
                )

                print(
                    "\n💬 NEW SLACK ACTIVITY"
                )

                print(
                    "User/Bot:",
                    user
                )

                print(
                    "Message:",
                    text[:200]
                )

                log_event(
                    "Slack",
                    "message_sent",
                    {
                        "channel": CHANNEL_NAME,
                        "message": text[:200],
                        "timestamp": timestamp
                    }
                )

            time.sleep(
                CHECK_INTERVAL
            )

        except KeyboardInterrupt:

            print(
                "\n🛑 Slack collector stopped."
            )
            break

        except Exception as e:

            print(
                "⚠️ Collector error:",
                e
            )

            time.sleep(
                CHECK_INTERVAL
            )


if __name__ == "__main__":
    main()