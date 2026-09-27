import os
import requests
from dotenv import load_dotenv

load_dotenv()

webhook_url = os.getenv("SLACK_WEBHOOK_URL")

message = {
    "text": """🔔 *WorkFlowOS Test Notification*

Customer: ABC Company
Request: Product quotation
Attachment: quotation.pdf
Status: New

🤖 WorkFlowOS successfully connected to Slack!"""
}

response = requests.post(
    webhook_url,
    json=message
)

if response.status_code == 200:
    print("✅ Slack notification sent successfully!")
else:
    print("❌ Slack error:", response.status_code)
    print(response.text)
