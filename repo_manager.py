#!/usr/bin/env python3
"""Module for dealing with git repos."""

import os
import argparse
from email.message import EmailMessage
from typing import Any
from typing import Tuple
from typing import Union

from git import Repo
import utils


class RepoInfo():
    """Repo information container."""

    def __init__(
        self,
        directory: str,
        url: str,
        name: str = None,
    ) -> None:
        """
        Constructor.

        :param directory: the directory that contains this repo
        :param name: the name to use as a reference
        :param url: the origin remote URL for the repo
        """
        self.dir = directory
        self.url = url
        if name is None:
            name = self._get_name_from_url(self.url)
        self.name = name
        self.path = os.path.join(self.dir, self.name)

    def _get_name_from_url(self, url: str) -> str:
        last_slash = url.rfind('/')
        name = url[(last_slash + 1):]
        # Make sure there is no .git ending
        name = name.strip('.git')
        return name


class RepoManager():
    """Class for managing local repos."""

    def __init__(
        self,
        repo_dir: str,
    ) -> None:
        """
        Constructor.

        :param repo_dir: the directory in which to put the repos
        """
        self._repo_dir = repo_dir
        self._repos = {}

    def clone(self, url: str) -> Tuple[Repo, RepoInfo]:
        """Clone a new repo."""
        info = RepoInfo(self._repo_dir, url)
        print(f"cloning repo '{info.name}' to: {info.path}")
        repo = Repo.clone_from(info.url, info.path)
        return repo, info

    def clone_from_email(self, msg: EmailMessage) -> Tuple[Union[Repo, None], Union[RepoInfo, None]]:
        url = utils.get_repo_url(msg.get_payload())
        if url is None:
            return None, None
        return self.clone(url)

    @classmethod
    def from_args(cls, args: Any):
        return RepoManager(args.repo_dir)


def add_args(parser: argparse.ArgumentParser) -> None:
    """Add repo managing args."""
    parser.add_argument(
        '--repo-dir', '-d',
        help='the directory in which to put the repos (default: %(default)s)',
        default='/tmp/repos')


def parse_args() -> Any:
    """Parse email polling arguments."""
    parser = argparse.ArgumentParser(description='Launch repo manager.')
    add_args(parser)
    return parser.parse_args()


def main() -> None:
    """Entrypoint for testing."""
    args = parse_args()
    manager = RepoManager(args.repo_dir)
    manager.clone('https://github.com/christophebedard/email2pr.git')


if __name__ == '__main__':
    main()
