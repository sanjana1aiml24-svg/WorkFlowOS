import os
import json
import time
import base64
from pathlib import Path

from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import requests

from crm import update_customer
from event_logger import log_event
from automation_state import automation_is_active


load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

GMAIL_USER = "workflowos.demo@gmail.com"
CUSTOMER_EMAIL = "customer011.demo@gmail.com"

ATTACHMENTS_DIR = Path("attachments")
ATTACHMENTS_DIR.mkdir(exist_ok=True)

PROCESSED_FILE = "processed_messages.json"

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")


def load_processed():
    try:
        with open(PROCESSED_FILE, "r") as f:
            return set(json.load(f))
    except Exception:
        return set()


def save_processed(processed):
    with open(PROCESSED_FILE, "w") as f:
        json.dump(list(processed), f, indent=2)


def get_gmail_service():
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    return build("gmail", "v1", credentials=creds)


def get_message_body(payload):
    body = payload.get("body", {})

    if body.get("data"):
        try:
            return base64.urlsafe_b64decode(
                body["data"].encode()
            ).decode("utf-8", errors="ignore")
        except Exception:
            pass

    for part in payload.get("parts", []):
        result = get_message_body(part)
        if result:
            return result

    return ""


def find_attachment_parts(payload):
    found = []

    if payload.get("filename") and payload.get("body", {}).get("attachmentId"):
        found.append(payload)

    for part in payload.get("parts", []):
        found.extend(find_attachment_parts(part))

    return found


def download_attachment(service, message_id, part):
    filename = part["filename"]
    attachment_id = part["body"]["attachmentId"]

    print(f"📎 Found attachment: {filename}")

    attachment = service.users().messages().attachments().get(
        userId="me",
        messageId=message_id,
        id=attachment_id
    ).execute()

    data = base64.urlsafe_b64decode(
        attachment["data"].encode()
    )

    output_path = ATTACHMENTS_DIR / filename

    # Avoid overwriting an existing file
    if output_path.exists():
        stem = output_path.stem
        suffix = output_path.suffix
        counter = 1

        while output_path.exists():
            output_path = ATTACHMENTS_DIR / f"{stem}-{counter}{suffix}"
            counter += 1

    with open(output_path, "wb") as f:
        f.write(data)

    print(f"✅ DOWNLOADED: {output_path}")

    log_event(
        "Gmail",
        "attachment_downloaded",
        {
            "filename": output_path.name
        }
    )

    return output_path


def send_slack(customer, subject, filename):
    if not SLACK_WEBHOOK_URL:
        print("⚠️ SLACK_WEBHOOK_URL not configured")
        return

    message = (
        "🔔 WorkFlowOS Automation\n\n"
        "New customer request processed\n\n"
        f"Customer: {customer}\n"
        "Request: Product quotation\n"
        f"Attachment: {filename}\n"
        "Status: Processed\n\n"
        "📎 Attachment downloaded\n"
        "🗄️ CRM updated\n"
        "🤖 Workflow completed automatically"
    )

    response = requests.post(
        SLACK_WEBHOOK_URL,
        json={"text": message},
        timeout=10
    )

    if response.ok:
        print("✅ Slack notification sent!")
        log_event(
            "Slack",
            "message_sent",
            {
                "channel": "#all-workflowos"
            }
        )
    else:
        print(f"⚠️ Slack error: {response.status_code}")


def process_message(service, message):
    message_id = message["id"]

    full_message = service.users().messages().get(
        userId="me",
        id=message_id,
        format="full"
    ).execute()

    payload = full_message.get("payload", {})

    headers = {
        h["name"].lower(): h["value"]
        for h in payload.get("headers", [])
    }

    sender = headers.get("from", "")
    subject = headers.get("subject", "Customer Request")

    # IMPORTANT:
    # Only process our demo customer.
    if CUSTOMER_EMAIL.lower() not in sender.lower():
        return False

    attachment_parts = find_attachment_parts(payload)

    # Only process emails containing an attachment.
    if not attachment_parts:
        return False

    print("\n📧 NEW CUSTOMER EMAIL DETECTED")
    print(f"From: {sender}")
    print(f"Subject: {subject}")

    body = get_message_body(payload)

    customer = "ABC Company"

    for line in body.splitlines():
        if line.lower().startswith("customer:"):
            customer = line.split(":", 1)[1].strip()
            break

    print("📎 Downloading attachment...")

    downloaded_file = None

    # Only download PDF attachments for the demo.
    for part in attachment_parts:
        filename = part["filename"]

        if filename.lower().endswith(".pdf"):
            downloaded_file = download_attachment(
                service,
                message_id,
                part
            )
            break

    if not downloaded_file:
        print("⚠️ No PDF attachment found. Ignoring email.")
        return False

    print("🗄️ Updating CRM...")

    crm_id = update_customer(
        name=customer,
        email=CUSTOMER_EMAIL,
        request="Product quotation",
        attachment=downloaded_file.name,
        status="Processed"
    )

    print(f"✅ CRM updated! ID: {crm_id}")

    print("💬 Sending Slack notification...")

    send_slack(
        customer,
        subject,
        downloaded_file.name
    )

    print("\n🎉 AUTOMATION COMPLETE!\n")

    return True


def get_customer_message_ids(service):
    result = service.users().messages().list(
        userId="me",
        q=f"from:{CUSTOMER_EMAIL} has:attachment"
    ).execute()

    return {
        msg["id"]
        for msg in result.get("messages", [])
    }


def main():

    print("=" * 55)
    print("🤖 WorkFlowOS Automation Monitor")
    print("=" * 55)

    service = get_gmail_service()

    processed = load_processed()

    # Snapshot all existing customer emails.
    # This prevents old demo emails from being processed again.
    existing_ids = get_customer_message_ids(service)

    processed.update(existing_ids)
    save_processed(processed)

    print("✅ Existing emails ignored.")
    print(f"📧 Monitoring: {CUSTOMER_EMAIL}")
    print("📎 PDF attachment processing: ON")
    print("💬 Slack notification: ON")
    print("⏳ Waiting for a NEW customer email...")
    print()

    while True:

        if not automation_is_active():
            print("⏸️ Automation not approved yet...")
            time.sleep(5)
            continue

        try:
            message_ids = get_customer_message_ids(service)

            new_messages = message_ids - processed

            for message_id in new_messages:

                message = {"id": message_id}

                success = process_message(
                    service,
                    message
                )

                processed.add(message_id)
                save_processed(processed)

            time.sleep(5)

        except Exception as e:
            print(f"⚠️ Monitor error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()