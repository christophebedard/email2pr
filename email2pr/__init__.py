"""Main module with higher-level logic for email2pr."""

import argparse
import sys
from typing import Any
from typing import List

from . import github
from . import params
from . import patch
from . import poller
from . import repo
from . import utils


class EmailToPr():
    """Main class with high-level API."""

    def __init__(self, args: Any) -> None:
        """Constructor."""
        self._manager = repo.RepoManager(args)
        email_info = poller.EmailConnectionInfo(args)
        self._poller = poller.EmailPoller(
            email_info,
            self._email_callback,
            ('SUBJECT', 'PATCH'),
        )

    def _email_callback(self, raw_email_data: List[Any]) -> None:
        """Execute logic, on new email."""
        print(f'===new email!====')
        try:
            msg = utils.email_from_raw_data(raw_email_data)
            # Clone repo
            # TODO maybe it already exists
            repo, info = self._manager.clone_from_email(msg)
            if repo is None or info is None:
                raise utils.EmailToPrError('no repo URL key!')
            # Create patch file in repo directory
            patch_filename, title, body = patch.from_email(msg, info.path)
            # Apply git patch to new branch
            pr_branch, base_branch = self._manager.apply_patch(repo, patch_filename)
            # Push to remote
            self._manager.push(repo)
            # Create PR
            pr_info = github.PrInfo(
                self._manager.repo_user,
                info.name,
                base_branch,
                pr_branch,
                title,
                body)
            url = github.create_pr(self._manager.repo_token, pr_info)
            print(f'PR created: {url}')
        except utils.EmailToPrError as e:
            print(f'email2pr error: {e}')

    def launch(self) -> None:
        """Launch polling of email server."""
        self._poller.poll()


def parse_args() -> Any:
    """Parse all email2pr args."""
    parser = argparse.ArgumentParser(description='Create GitHub PRs from patch emails.')
    poller.add_args(parser)
    repo.add_args(parser)
    return parser.parse_args()


def main(argv=sys.argv) -> None:
    """Do setup for email2pr."""
    args = None
    if len(argv) == 1:
        args = params.Params('params.yaml')
        args.assert_params_defined([
            'email_user',
            'email_pass',
            'repo_user',
            'repo_token',
        ])
    else:
        args = parse_args()
    etopr = EmailToPr(args)
    etopr.launch()
