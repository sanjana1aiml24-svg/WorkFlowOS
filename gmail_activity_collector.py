import time
import json
import os
from pathlib import Path

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from event_logger import log_event

TOKEN_FILE = "token.json"
SEEN_FILE = "gmail_seen.json"

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

DOWNLOAD_DIR = Path.home() / "Downloads"
CHECK_INTERVAL = 2

IGNORE_SENDERS = [
    "no-reply@google.com",
    "noreply-accounts@google.com",
    "no-reply@slack.com",
    "slack.com"
]

IGNORE_SUBJECTS = [
    "finish setting up",
    "you shared some google account data",
    "started a free trial",
    "new account details"
]


def load_seen():
    if not os.path.exists(SEEN_FILE):
        return []

    try:
        with open(SEEN_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []


def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(seen, f, indent=2)


def get_service():
    credentials = Credentials.from_authorized_user_file(
        TOKEN_FILE,
        SCOPES
    )

    return build("gmail", "v1", credentials=credentials)


def get_messages(service):
    response = service.users().messages().list(
        userId="me",
        q="in:inbox newer_than:1d",
        maxResults=20
    ).execute()

    return response.get("messages", [])


def get_message(service, message_id):
    return service.users().messages().get(
        userId="me",
        id=message_id,
        format="full"
    ).execute()


def get_header(headers, name):
    for header in headers:
        if header["name"].lower() == name.lower():
            return header["value"]

    return ""


def is_relevant(sender, subject):
    sender_lower = sender.lower()
    subject_lower = subject.lower()

    for ignored in IGNORE_SENDERS:
        if ignored in sender_lower:
            return False

    for ignored in IGNORE_SUBJECTS:
        if ignored in subject_lower:
            return False

    return True


def get_attachment_names(part):
    names = []

    filename = part.get("filename", "")

    if filename:
        names.append(filename)

    for child in part.get("parts", []):
        names.extend(get_attachment_names(child))

    return names


def get_download_files():
    if not DOWNLOAD_DIR.exists():
        return {}

    files = {}

    try:
        for file in DOWNLOAD_DIR.iterdir():
            if file.is_file():
                try:
                    files[file.name] = file.stat().st_mtime
                except OSError:
                    pass
    except OSError:
        pass

    return files


def main():

    print("=" * 65)
    print("🧠 WorkFlowOS REAL GMAIL ACTIVITY COLLECTOR")
    print("=" * 65)
    print("Watching REAL Gmail activity + REAL local downloads.")
    print()
    print("Detected actions:")
    print("  📧 Email opened/received")
    print("  📥 Actual file downloaded to Downloads")
    print()
    print("Press Ctrl+C to stop.\n")

    service = get_service()

    seen = load_seen()

    print(f"👀 Existing emails ignored: {len(seen)}")

    previous_downloads = get_download_files()

    print(f"📁 Monitoring: {DOWNLOAD_DIR}")
    print("🔄 Waiting for new activity...\n")

    while True:

        try:

            messages = get_messages(service)

            for item in reversed(messages):

                message_id = item["id"]

                if message_id in seen:
                    continue

                message = get_message(
                    service,
                    message_id
                )

                payload = message.get(
                    "payload",
                    {}
                )

                headers = payload.get(
                    "headers",
                    []
                )

                sender = get_header(
                    headers,
                    "From"
                )

                subject = get_header(
                    headers,
                    "Subject"
                )

                seen.append(message_id)
                save_seen(seen)

                if not is_relevant(
                    sender,
                    subject
                ):
                    print("⏭️ Ignored:", subject)
                    continue

                attachment_names = get_attachment_names(
                    payload
                )

                print("\n📧 REAL EMAIL ACTIVITY")
                print("From:", sender)
                print("Subject:", subject)

                log_event(
                    "Gmail",
                    "email_read",
                    {
                        "message_id": message_id,
                        "subject": subject,
                        "sender": sender
                    }
                )

                if attachment_names:

                    print(
                        "📎 Attachment detected:",
                        ", ".join(attachment_names)
                    )

                    print(
                        "👀 Waiting for ACTUAL download..."
                    )

                else:

                    print("📭 No attachment")

            current_downloads = get_download_files()

            for filename in current_downloads:

                if filename not in previous_downloads:

                    print("\n📥 REAL DOWNLOAD DETECTED")
                    print("File:", filename)

                    log_event(
                        "Gmail",
                        "attachment_downloaded",
                        {
                            "filename": filename,
                            "path": str(
                                DOWNLOAD_DIR / filename
                            )
                        }
                    )

            previous_downloads = current_downloads

            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:

            print(
                "\n🛑 Gmail activity collector stopped."
            )
            break

        except Exception as e:

            print(
                "⚠️ Collector error:",
                e
            )

            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
