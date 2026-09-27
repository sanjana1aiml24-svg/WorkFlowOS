from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import os
import base64


SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def get_gmail_service():

    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file(
            "token.json",
            SCOPES
        )

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES
            )

            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build(
        "gmail",
        "v1",
        credentials=creds
    )


# Connect to Gmail
service = get_gmail_service()

print("\n📧 Searching for customer email...\n")


# Find customer email
results = service.users().messages().list(
    userId="me",
    q="in:anywhere from:customer011.demo@gmail.com",
    maxResults=1
).execute()

messages = results.get("messages", [])


if not messages:

    print("❌ Customer email not found.")

else:

    message_id = messages[0]["id"]

    message = service.users().messages().get(
        userId="me",
        id=message_id,
        format="full"
    ).execute()

    print("✅ Customer email found!")
    print("Message ID:", message_id)

    # Create attachment folder
    os.makedirs("attachments", exist_ok=True)

    parts = message["payload"].get("parts", [])

    attachment_found = False

    for part in parts:

        filename = part.get("filename")

        body = part.get("body", {})

        attachment_id = body.get("attachmentId")


        if filename and attachment_id:

            print("\n📎 Attachment found:")
            print("Filename:", filename)

            attachment = service.users().messages().attachments().get(
                userId="me",
                messageId=message_id,
                id=attachment_id
            ).execute()

            file_data = attachment["data"]

            file_data = base64.urlsafe_b64decode(
                file_data
            )

            file_path = os.path.join(
                "attachments",
                filename
            )

            with open(file_path, "wb") as file:

                file.write(file_data)

            print("✅ Downloaded:", file_path)

            attachment_found = True


    if not attachment_found:

        print("\n⚠️ No attachment found.")

    else:

        print("\n🎉 Attachment successfully downloaded!")
