#!/usr/bin/env python3

"""Module with higher-level logic for email2pr."""

import argparse
from typing import Any
from typing import List

import email_poller

from email_to_patch import email_to_patch

import repo_manager

import utils


class EmailToPr():
    """Main class with high-level API."""

    def __init__(self, args: Any) -> None:
        """Constructor."""
        self._manager = repo_manager.RepoManager.from_args(args)
        email_info = email_poller.EmailConnectionInfo.from_args(args)
        self._poller = email_poller.EmailPoller(
            email_info,
            self._email_callback,
            ('SUBJECT', 'PATCH'),
        )

    def _email_callback(self, raw_email_data: List[Any]) -> None:
        """Execute logic, on new email."""
        print(f'===new email!====')
        msg = msg = utils.email_from_raw_data(raw_email_data)
        # Clone repo
        # TODO maybe it already exists
        repo, info = self._manager.clone_from_email(msg)
        if repo is None or info is None:
            print('No repo URL key!')
            return None
        # Create patch file, add to repo directory
        patch_filename = email_to_patch(msg, info.path)
        # TODO
        # Create new branch
        # Apply git patch
        # Push to remote
        # Create PR

    def poll(self) -> None:
        """Launch polling of email server."""
        self._poller.poll()


def parse_args() -> Any:
    """Parse all email2pr args."""
    parser = argparse.ArgumentParser(description='Create GitHub PRs from patch emails.')
    email_poller.add_args(parser)
    repo_manager.add_args(parser)
    return parser.parse_args()


def main() -> None:
    """Do setup for email2pr."""
    args = parse_args()
    etopr = EmailToPr(args)
    etopr.poll()


if __name__ == '__main__':
    main()
