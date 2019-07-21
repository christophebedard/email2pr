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


def get_parser() -> argparse.ArgumentParser:
    """Parse all email2pr args."""
    parser = argparse.ArgumentParser(
        description='Create GitHub PRs from patch emails.',
        epilog=(
            'Instead of this, you can also simply provide a .yaml '
            'param file name instead (default: params.yaml)'
        ),
        parents=[
            poller.get_parser(),
            repo.get_parser(),
        ]
    )
    return parser


def get_params(argv) -> Any:
    args = None
    # If all arguments given, or if help wanted,
    # use argparse, else use parameters file
    is_help = len(argv) == 2 and argv[1] in ['-h', '--help']
    if len(argv) > 2 or is_help:
        args = get_parser().parse_args()
    else:
        params_file = argv[1] if len(argv) == 2 else None
        args = params.Params(params_file)
        args.assert_params_defined([
            'email_user',
            'email_pass',
            'repo_user',
            'repo_token',
        ])
    return args


def main(argv=sys.argv) -> None:
    """Do setup for email2pr."""
    args = get_params(argv)
    etopr = EmailToPr(args)
    etopr.launch()
