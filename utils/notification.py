# utils/notification.py
import firebase_admin
from firebase_admin import credentials, messaging
import os

# Load credentials only once
if not firebase_admin._apps:
    cred = credentials.Certificate("services/serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

def send_firebase_notification_v1(token, title, body, data=None):
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=token,
        data=data or {},
    )

    response = messaging.send(message)
    return response
