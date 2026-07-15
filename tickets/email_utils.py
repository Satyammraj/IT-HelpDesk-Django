import os
import requests


def send_email(subject, message, recipients):
    url = "https://api.brevo.com/v3/smtp/email"

    headers = {
        "accept": "application/json",
        "api-key": os.environ.get("BREVO_API_KEY"),
        "content-type": "application/json",
    }

    payload = {
        "sender": {
            "name": "IT Help Desk",
            "email": "samd89544@gmail.com",   # Verified sender in Brevo
        },
        "to": [{"email": email} for email in recipients],
        "subject": subject,
        "textContent": message,
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()