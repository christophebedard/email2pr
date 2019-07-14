#!/usr/bin/env python3
"""Module for email polling."""

import argparse
import time
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Tuple
from typing import Union

import email
from imaplib import IMAP4_SSL
from imaplib import IMAP4_SSL_PORT

from email_to_patch import patch_from_email


class EmailConnectionInfo():
    """Email connection information wrapper."""

    def __init__(
        self,
        email_user: str,
        email_pass: str,
        email_host: str,
        email_port: int = IMAP4_SSL_PORT,
    ) -> None:
        self.user = email_user
        self.passw = email_pass
        self.host = email_host
        self.port = email_port


class EmailPoller():
    """Email polling interface."""

    def __init__(
        self,
        email_info: EmailConnectionInfo,
        callback: Callable[[List[Any]], None],
        search_args: Tuple[Union[str, None], str] = (None, 'ALL'),
    ) -> None:
        self._info = email_info
        self._callback = callback
        self._search_args = search_args

    def _get_server(self) -> IMAP4_SSL:
        """Login and return server object."""
        server = IMAP4_SSL(self._info.host, self._info.port)
        result, _ = server.login(self._info.user, self._info.passw)
        assert result == 'OK', 'login failed!'
        return server

    def _get_email_uids(self) -> List[bytes]:
        """Get all email uids."""
        server = self._get_server()
        server.select('"[Gmail]/All Mail"')
        arg_first, arg_second = self._search_args
        result, data = server.uid('search', arg_first, arg_second)
        assert result == 'OK', 'uid() failed!'
        ids = data[0].split()
        server.logout()
        return ids

    def _get_latest_uid(self) -> bytes:
        """Get latest email uid."""
        ids = self._get_email_uids()
        return max(ids)

    def _get_email_from_uid(self, uid: bytes) -> List[Any]:
        """Get an email corresponding to a uid."""
        server = self._get_server()
        server.select('"[Gmail]/All Mail"')
        result, data = server.uid('fetch', uid, '(RFC822)')
        assert result == 'OK', 'uid() failed!'
        server.logout()
        return data

    def _process_new_email(self, raw_email_data: List[Any]) -> None:
        self._callback(raw_email_data)

    def poll(self, period_s: int = 5) -> None:
        """
        Poll email server for new emails.

        :param period_seconds: the number of seconds to wait before polling again
        """
        # Get uid of latest email
        print('getting latest email..')
        last_uid = self._get_latest_uid()

        while True:
            print('polling emails..')

            # Get all emails
            uids = self._get_email_uids()
            for uid in uids:
                # Check if new
                if uid > last_uid:
                    last_uid = uid
                    raw_email_data = self._get_email_from_uid(uid)
                    self._process_new_email(raw_email_data)

            time.sleep(period_s)


def parse_args():
    parser = argparse.ArgumentParser(description='Launch email poller.')
    parser.add_argument(
        'email_user',
        help='the email account username')
    parser.add_argument(
        'email_pass',
        help='the email account password')
    parser.add_argument(
        '--email-host', '-a',
        help='the email host address (default: %(default)s)',
        default='imap.gmail.com')
    parser.add_argument(
        '--email-port', '-p',
        help='the port number (default: %(default)s)',
        default=IMAP4_SSL_PORT)
    return parser.parse_args()


def test_callback(raw_email_data: List[Any]) -> None:
    print(f'===new email!====')
    email_string = raw_email_data[0][1].decode('utf-8')
    msg = email.message_from_string(email_string)
    patch_from_email(msg, '/tmp')


def main():
    args = parse_args()
    info = EmailConnectionInfo(
        args.email_user,
        args.email_pass,
        args.email_host,
        args.email_port,
    )
    poller = EmailPoller(
        info,
        test_callback,
        ('SUBJECT', 'PATCH'),
    )
    poller.poll()


if __name__ == '__main__':
    main()
