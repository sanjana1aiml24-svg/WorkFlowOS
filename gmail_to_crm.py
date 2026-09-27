import os
import base64
import json

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from crm import update_customer
from event_logger import log_event


SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


print("🚀 WorkFlowOS")
print("GMAIL → UNDERSTAND → ATTACHMENT → CRM → SLACK\n")


# -------------------------
# CONNECT TO GMAIL
# -------------------------

print("📧 Checking Gmail...")

creds = Credentials.from_authorized_user_file(
    "token.json",
    SCOPES
)

gmail = build(
    "gmail",
    "v1",
    credentials=creds
)


# -------------------------
# FIND CUSTOMER EMAIL
# -------------------------

results = gmail.users().messages().list(
    userId="me",
    q="in:anywhere from:customer011.demo@gmail.com"
).execute()

messages = results.get("messages", [])

if not messages:
    print("❌ No customer email found.")
    exit()

message_id = messages[0]["id"]

message = gmail.users().messages().get(
    userId="me",
    id=message_id,
    format="full"
).execute()


print("✅ Customer email found!")

log_event(
    "Gmail",
    "email_read"
)


# -------------------------
# READ EMAIL
# -------------------------

headers = message["payload"].get("headers", [])

subject = ""

for header in headers:
    if header["name"].lower() == "subject":
        subject = header["value"]


customer_name = "ABC Company"
request = "Product quotation"


print("\n🤖 WorkFlowOS Understanding")
print(f"Customer: {customer_name}")
print(f"Email: customer011.demo@gmail.com")
print(f"Request: {request}")
print(f"Subject: {subject}")


# -------------------------
# DOWNLOAD ATTACHMENT
# -------------------------

print("\n📎 Processing attachments...")

attachment_found = False
filename = None

def process_parts(parts):

    global attachment_found
    global filename

    for part in parts:

        if part.get("filename"):

            filename = part["filename"]

            if part.get("body", {}).get("attachmentId"):

                attachment_id = part["body"]["attachmentId"]

                attachment = gmail.users().messages().attachments().get(
                    userId="me",
                    messageId=message_id,
                    id=attachment_id
                ).execute()

                data = attachment["data"]

                file_data = base64.urlsafe_b64decode(data)

                os.makedirs("attachments", exist_ok=True)

                filepath = os.path.join(
                    "attachments",
                    filename
                )

                with open(filepath, "wb") as f:
                    f.write(file_data)

                print(f"✅ Downloaded: {filename}")

                log_event(
                    "Gmail",
                    "attachment_downloaded",
                    {"filename": filename}
                )

                attachment_found = True

        if part.get("parts"):
            process_parts(part["parts"])


process_parts(
    message["payload"].get("parts", [])
)


if not attachment_found:
    print("⚠️ No attachment found.")


# -------------------------
# UPDATE CRM
# -------------------------

print("\n🗄️ Updating CRM...")

try:

    record_id = update_customer(
        customer_name,
        "customer011.demo@gmail.com",
        request,
        filename if filename else "",
        "Processed"
    )

    print(f"🔄 CRM record updated! ID: {record_id}")

    log_event(
        "CRM",
        "customer_updated",
        {
            "customer": customer_name,
            "record_id": record_id
        }
    )

except Exception as e:

    print("❌ CRM error:", e)


# -------------------------
# SLACK NOTIFICATION
# -------------------------

print("\n💬 Sending Slack notification...")

from dotenv import load_dotenv
import requests

load_dotenv()

webhook_url = os.getenv("SLACK_WEBHOOK_URL")

slack_message = {
    "text": f"""🔔 *WorkFlowOS Automation*

Customer: {customer_name}
Request: {request}
Attachment: {filename}
Status: Processed

📎 Attachment downloaded
🗄️ CRM updated
🤖 Workflow completed"""
}

response = requests.post(
    webhook_url,
    json=slack_message
)

if response.status_code == 200:

    print("✅ Slack notification sent!")

    log_event(
        "Slack",
        "notification_sent",
        {"customer": customer_name}
    )

else:

    print("❌ Slack error:", response.status_code)


print("\n🎉 REAL WORKFLOW COMPLETE!")