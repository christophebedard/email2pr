"""Module for converting emails to patch files."""

import os
from email.message import EmailMessage
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


def _crlf_to_lf(file_path: str) -> None:
    """
    Convert file to LF only.

    :param file_path: the file to convert
    """
    contents = open(file_path, 'r').read()
    f = open(file_path, 'w', newline='\n')
    f.write(contents)
    f.close()


def from_email(
    msg: EmailMessage,
    dest_path: str,
) -> Tuple[str, str, str]:
    """
    Create a patch file from a patch email.

    :param msg: the email message
    :param dest_path: the directory in which to create the patch file
    :return: (the file name of the created patch file,
        the title of the patch,
        the body of the patch)
    """
    msg_from = msg['from']
    msg_date = msg['date']
    msg_subject = msg['subject']
    msg_payload = msg.get_payload()

    index, total = _get_patch_index(msg_subject)
    patch_title = _get_patch_title(msg_subject)
    file_name = f'{index:04}-{patch_title}.patch'

    # To be valid, there has to be a hash on the
    # first line, even if it doesn't mean anything
    fake_hash = '0' * 40

    full_path = os.path.join(dest_path, file_name)
    with open(full_path, 'w') as f:
        f.writelines([
            f'From: {fake_hash}\n',
            f'From: {msg_from}\n',
            f'Date: {msg_date}\n',
            f'Subject: {msg_subject}\n',
            '\n',
            msg_payload,
        ])
    _crlf_to_lf(full_path)

    # The body of the commit is before the first '---'
    patch_body = msg_payload[:msg_payload.find('\n---')]
    return file_name, patch_title, patch_body
