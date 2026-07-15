import os
import requests


def send_brevo_email(subject, message, from_email=None, recipient_list=None, fail_silently=False):
    headers = {
        "accept": "application/json",
        "api-key": os.environ.get("BREVO_API_KEY"),
        "content-type": "application/json",
    }

    payload = {
        "sender": {
            "name": "IT Help Desk",
            "email": "samd89544@gmail.com",
        },
        "to": [{"email": email} for email in recipient_list],
        "subject": subject,
        "textContent": message,
    }

    try:
        response = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            headers=headers,
            json=payload,
            timeout=10,
        )
        response.raise_for_status()
        return 1
    except Exception:
        if not fail_silently:
            raise
        return 0