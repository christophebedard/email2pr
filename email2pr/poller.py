"""Module for email polling."""

import argparse
import time
from imaplib import IMAP4_SSL
from imaplib import IMAP4_SSL_PORT
from typing import Any
from typing import Callable
from typing import List
from typing import Tuple
from typing import Union

from . import patch
from . import utils


class EmailConnectionInfo():
    """Email connection information wrapper."""

    def __init__(
        self,
        params: Any,
    ) -> None:
        """Constructor."""
        self.user = params.email_user
        self.passw = params.email_pass
        self.host = params.email_host if params.email_host is not None else 'imap.gmail.com'
        self.port = params.email_port if params.email_port is not None else IMAP4_SSL_PORT


class EmailPoller():
    """Email polling interface."""

    def __init__(
        self,
        email_info: EmailConnectionInfo,
        callback: Callable[[List[Any]], None],
        search_args: Tuple[Union[str, None], str] = (None, 'ALL'),
    ) -> None:
        """Constructor."""
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


def add_args(parser: argparse.ArgumentParser) -> None:
    """Add email polling args."""
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


def parse_args() -> Any:
    """Parse email polling arguments."""
    parser = argparse.ArgumentParser(description='Launch email poller.')
    add_args(parser)
    return parser.parse_args()


def _test_callback(raw_email_data: List[Any]) -> None:
    print(f'===new email!====')
    msg = utils.email_from_raw_data(raw_email_data)
    patch.from_email(msg, '/tmp')


def main() -> None:
    """Email polling entrypoint for testing."""
    args = parse_args()
    info = EmailConnectionInfo(args)
    poller = EmailPoller(
        info,
        _test_callback,
        ('SUBJECT', 'PATCH'),
    )
    poller.poll()


if __name__ == '__main__':
    main()
