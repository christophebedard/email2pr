"""Module for converting emails to patch files."""

from email.message import EmailMessage
import os
from typing import Tuple


def _get_patch_index(subject: str) -> Tuple[int, int]:
    """
    Get index of patch and the total number of related patches.

    :param subject: the email subject
    :return: (patch index, total)
    """
    # Extract [PATCH ...] substring
    patch_start = subject.find('PATCH')
    bracket_open = subject.find('[', 0, patch_start)
    bracket_close = subject.find(']', bracket_open)
    patch_string = subject[(bracket_open + 1):bracket_close]
    # No numbers if there's only one
    if patch_string == 'PATCH':
        return 1, 1
    else:
        patch_number_sep = patch_string.find('/')
        index = int(patch_string[patch_number_sep - 1])
        total = int(patch_string[patch_number_sep + 1])
        return index, total


def _get_patch_title(subject: str) -> str:
    """
    Get formatted patch title/filename from patch email subject.

    :param subject: the email subject
    :return: the formatted patch filename
    """
    bracket_close = subject.find(']')
    title = subject[(bracket_close + 1):]
    title = title.strip()
    title = title.replace(' ', '-')
    return title


def email_to_patch(msg: EmailMessage, dest_path: str):
    """
    Create a patch file from a patch email.

    :param msg: the email message
    :param dest_path: the directory in which to create the patch file
    """
    msg_from = msg["from"]
    msg_data = msg["date"]
    msg_subject = msg["subject"]
    msg_payload = msg.get_payload()

    index, total = _get_patch_index(msg_subject)
    patch_title = _get_patch_title(msg_subject)
    file_name = f'{index:04}-{patch_title}.patch'

    full_path = os.path.join(dest_path, file_name)
    with open(full_path, 'w') as f:
        f.write(f'From: {msg_from}\n')
        f.write(f'Date: {msg_data}\n')
        f.write(f'Subject: {msg_subject}\n')
        f.write('\n')
        f.write(msg_payload)
