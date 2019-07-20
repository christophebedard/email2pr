"""Module for utilities."""

import email
from email.message import EmailMessage
from typing import Any
from typing import List
from typing import Union


def email_from_raw_data(raw_email_data: List[Any]) -> EmailMessage:
    """Get email message from raw data."""
    email_string = raw_email_data[0][1].decode('utf-8')
    msg = email.message_from_string(email_string)
    return msg


def get_key_value(body: str, key: str) -> Union[str, None]:
    """
    Extract value for a given key.

    :param body: the body in which to search
    :param key: the key to look for
    :return: the URL value, or `None` if not found
    """
    url = None
    for line in body.splitlines():
        if line.startswith(key):
            sep_index = line.find(':')
            url = line[(sep_index + 1):].strip()
    return url


def get_repo_url(body: str) -> Union[str, None]:
    """
    Extract repo URL value from body.

    :param body: the body in which to search
    :return: the URL value, or `None` if not found
    """
    return get_key_value(body, 'Github-Repo-Url')


def get_target_branch(body: str) -> Union[str, None]:
    """
    Extract target branch value from body.

    :param body: the body in which to search
    :return: the target branch value, or `None` if not found
    """
    return get_key_value(body, 'Target-Branch')