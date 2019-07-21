"""Module for utilities."""

import email
from email.message import EmailMessage
from typing import Any
from typing import List
from typing import Union

KEY_REPO_URL = 'Github-Repo-Url'
KEY_BASE_BRANCH = 'Target-Branch'


class EmailToPrError(Exception):
    """General class for email2pr error."""

    def __init__(
        self,
        msg: str,
        exception: Union[Exception, None] = None,
    ) -> None:
        if exception is not None:
            original_msg = str(exception).replace('\n', '\n\t')
            msg += '\n\t' + original_msg
        super().__init__(msg)


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
    return get_key_value(body, KEY_REPO_URL)


def get_target_branch(body: str) -> Union[str, None]:
    """
    Extract target branch value from body.

    :param body: the body in which to search
    :return: the target branch value, or `None` if not found
    """
    return get_key_value(body, KEY_BASE_BRANCH)


def insert_token_in_remote_url(
    url: str,
    user: str,
    token: str,
) -> str:
    """
    Insert authentication token into remote URL.

    This assumes that the URL includes '://'.

    :param url: the original URL
    :param user: the username
    :param token: the token
    :return: the URL with the inserted username and password
    """
    SEP = '://'
    index = url.find(SEP) + len(SEP)
    return url[:index] + user + ':' + token + '@' + url[index:]
