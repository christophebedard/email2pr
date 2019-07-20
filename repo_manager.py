#!/usr/bin/env python3
"""Module for dealing with git repos."""

import argparse
import os
import time
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
        target_branch: str = None,
        name: str = None,
    ) -> None:
        """
        Constructor.

        :param directory: the directory that contains this repo
        :param url: the origin remote URL for the repo
        :param target_branch: the name of the branch to use, or `None` for default
        :param name: the name to use as a reference, or `None` to extract from repo URL
        """
        self.dir = directory
        self.url = url
        if name is None:
            name = self._get_name_from_url(self.url)
        self.name = name
        self.branch = target_branch
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

    def clone(
        self,
        info: RepoInfo,
    ) -> Union[Repo, None]:
        """
        Clone a new repo, selecting a specific branch if given.
        
        :param info: the information of the repo to clone
        :return: the cloned repo object, or `None` if it failed
        """
        print(f"cloning repo '{info.name}' to: {info.path}")
        repo = None
        if info.branch is None:
            repo = Repo.clone_from(info.url, info.path)
        else:
            repo = Repo.clone_from(info.url, info.path, branch=info.branch)
        return repo

    def clone_from_email(
        self,
        msg: EmailMessage,
    ) -> Tuple[Union[Repo, None], Union[RepoInfo, None]]:
        """
        Clone repo corresponding to email and checkout target branch.

        :param msg: the email message
        :return: (repo, repo information) or (`None`, `None`) if email has no URL
        """
        # URL is mandatory
        url = utils.get_repo_url(msg.get_payload())
        if url is None:
            return None, None
        # Target branch is not mandatory
        target_branch = utils.get_target_branch(msg.get_payload())
        info = RepoInfo(self._repo_dir, url, target_branch)
        return self.clone(info), info

    def apply_patch(
        self,
        repo: Repo,
        info: RepoInfo,
        patch_filename: str,
    ) -> None:
        """
        Apply patch to repo.
        """
        # Create new branch from the current one
        current_branch_name = repo.active_branch
        new_branch_name = f'{current_branch_name}-{time.strftime("%Y%m%d%H%M%S")}'
        print(f"creating new branch '{new_branch_name}' from branch '{current_branch_name}'")
        new_branch = repo.create_head(new_branch_name)
        print('switching to new branch')
        repo.head.reference = new_branch

        # Apply patch file
        # TODO

    @classmethod
    def from_args(cls, args: Any):
        """Create RepoManager instance from parsed arguments."""
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
    info = RepoInfo(args.repo_dir, 'https://github.com/christophebedard/email2pr.git', 'master')
    repo = manager.clone(info)
    manager.apply_patch(repo, info, 'todo')


if __name__ == '__main__':
    main()
