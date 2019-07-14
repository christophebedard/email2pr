#!/usr/bin/env python3
"""Module for email polling."""

import argparse
import time
from typing import List
from typing import Tuple
from typing import Dict

import email
from imaplib import IMAP4_SSL
from imaplib import IMAP4_SSL_PORT


class EmailPoller():
    """Email polling interface."""

    def __init__(
        self,
        email_user: str,
        email_pass: str,
        email_host: str,
        email_port: int = IMAP4_SSL_PORT,
        subject_search: str = 'PATCH',
    ) -> None:
        self._email_user = email_user
        self._email_pass = email_pass
        self._email_host = email_host
        self._email_port = email_port
        self._subject_search = subject_search

    def _get_server(self) -> IMAP4_SSL:
        """Login and return server object."""
        server = IMAP4_SSL(self._email_host, self._email_port)
        result, _ = server.login(self._email_user, self._email_pass)
        assert result == 'OK', 'login failed!'
        return server

    def _get_email_uids(self) -> Tuple[List[int], Dict]:
        """Get all email uids."""
        server = self._get_server()
        server.select('"[Gmail]/All Mail"')
        result, data = server.uid('search', 'SUBJECT', self._subject_search)
        assert result == 'OK', 'uid() failed!'
        ids = data[0].split()
        server.logout()
        return ids

    def _get_latest_uid(self):
        """Get latest email uid."""
        ids = self._get_email_uids()
        return max(ids)

    def _get_email_from_uid(self, uid: int):
        """Get an email corresponding to a uid."""
        server = self._get_server()
        server.select('"[Gmail]/All Mail"')
        result, data = server.uid('fetch', uid, '(RFC822)')
        assert result == 'OK', 'uid() failed!'
        server.logout()
        return data

    def _process_new_email(self, raw_data):
        # TODO
        print(f'new email! --> \n{raw_data}')

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
                    raw_email = self._get_email_from_uid(uid)
                    self._process_new_email(raw_email)

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
        help='the email host address',
        default='imap.gmail.com')
    parser.add_argument(
        '--email-port', '-p',
        help='the port number',
        default=IMAP4_SSL_PORT)
    return parser.parse_args()


def main():
    args = parse_args()
    poller = EmailPoller(
        args.email_user,
        args.email_pass,
        args.email_host,
        args.email_port,
    )
    poller.poll()


if __name__ == '__main__':
    main()
