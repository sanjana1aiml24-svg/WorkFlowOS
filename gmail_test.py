from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
import base64

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def get_service():
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

    return build("gmail", "v1", credentials=creds)


def get_email_body(payload):
    """
    Extract the text body from a Gmail message.
    """

    # Simple email
    if payload.get("body", {}).get("data"):
        data = payload["body"]["data"]
        return base64.urlsafe_b64decode(data).decode(
            "utf-8",
            errors="ignore"
        )

    # Multipart email
    for part in payload.get("parts", []):
        if part["mimeType"] == "text/plain":
            data = part.get("body", {}).get("data")

            if data:
                return base64.urlsafe_b64decode(data).decode(
                    "utf-8",
                    errors="ignore"
                )

        # Check nested parts
        if part.get("parts"):
            body = get_email_body(part)

            if body:
                return body

    return ""


# Connect to Gmail
service = get_service()

print("\n📧 WorkFlowOS Gmail Reader\n")

# Search everywhere, including Spam
results = service.users().messages().list(
    userId="me",
    q="in:anywhere from:customer011.demo@gmail.com",
    maxResults=10
).execute()

messages = results.get("messages", [])

if not messages:
    print("❌ Customer email not found.")
else:

    print(f"✅ Found {len(messages)} email(s)!\n")

    for message in messages:

        msg = service.users().messages().get(
            userId="me",
            id=message["id"],
            format="full"
        ).execute()

        headers = msg["payload"]["headers"]

        sender = ""
        recipient = ""
        subject = ""

        for header in headers:

            name = header["name"]
            value = header["value"]

            if name.lower() == "from":
                sender = value

            elif name.lower() == "to":
                recipient = value

            elif name.lower() == "subject":
                subject = value

        body = get_email_body(msg["payload"])

        print("--------------------------------")
        print("📨 From:", sender)
        print("📬 To:", recipient)
        print("📝 Subject:", subject)
        print("\n📄 Email Body:")
        print(body)

        print("\n🆔 Message ID:", message["id"])

        # Extract customer name
        customer_name = ""

        for line in body.splitlines():

            if line.strip().lower().startswith("customer:"):
                customer_name = line.split(":", 1)[1].strip()

        # Extract request
        request = ""

        if "quotation" in subject.lower() or "quotation" in body.lower():
            request = "Product quotation"

        print("\n🤖 WorkFlowOS Understanding")
        print("Customer:", customer_name)
        print("Request:", request)

        print("\n✅ Email successfully understood!")