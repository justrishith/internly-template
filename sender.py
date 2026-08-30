"""
Gmail sender.
Uses refresh token to get access token, then sends via Gmail API.
"""

import json
import os
import base64
from email.mime.text import MIMEText

def get_access_token(refresh_token: str, client_id: str, client_secret: str) -> str:
    """Exchange refresh token for access token."""
    import requests

    resp = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]

def send_email(to: str, subject: str, body: str, config) -> bool:
    """Send an email via Gmail API using refresh token."""
    import requests

    refresh_token = os.getenv("GOOGLE_REFRESH_TOKEN", "")
    if not refresh_token:
        print("No GOOGLE_REFRESH_TOKEN set. Cannot send.")
        return False

    try:
        # Get fresh access token
        access_token = get_access_token(
            refresh_token,
            config.gmail_client_id,
            config.gmail_client_secret,
        )

        # Build email
        msg = MIMEText(body)
        msg["to"] = to
        msg["from"] = "me"  # Gmail replaces with authenticated email
        msg["subject"] = subject

        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

        # Send via Gmail API
        resp = requests.post(
            "https://gmail.googleapis.com/gmail/v1/users/me/messages/send",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"raw": raw},
            timeout=30,
        )

        if resp.status_code == 200:
            return True

        print(f"Gmail API error: {resp.status_code} - {resp.text[:200]}")
        return False

    except Exception as e:
        print(f"Send error: {e}")
        return False
