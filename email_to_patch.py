"""Module for converting emails to patch files."""

from email.message import EmailMessage
import os


def patch_from_email(msg: EmailMessage, dest_path: str):
    msg_from = msg["from"]
    msg_data = msg["date"]
    msg_subject = msg["subject"]
    msg_payload = msg.get_payload()
    file_name = 'patch.patch'

    full_path = os.path.join(dest_path, file_name)
    with open(full_path, 'w') as f:
        f.write(f'From: {msg_from}\n')
        f.write(f'Date: {msg_data}\n')
        f.write(f'Subject: {msg_subject}\n')
        f.write('\n')
        f.write(msg_payload)
