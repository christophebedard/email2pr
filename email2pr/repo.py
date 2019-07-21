"""Module for dealing with git repos."""

import argparse
import os
import shlex
import subprocess
import time
from email.message import EmailMessage
from typing import Any
from typing import Tuple
from typing import Union

from git import GitError
from git import Repo

from . import utils


class RepoInfo():
    """Repo information container."""

    def __init__(
        self,
        directory: str,
        url: str,
        base_branch: str = None,
        name: str = None,
    ) -> None:
        """
        Constructor.

        :param directory: the directory that contains this repo
        :param url: the origin remote URL for the repo ('.git' suffix is optional)
        :param base_branch: the name of the base branch to use, or `None` for default
        :param name: the name to use as a reference, or `None` to extract from repo URL
        """
        self.dir = directory if directory is not None else '/tmp/repos'
        self.url = utils.add_git_suffix(url)
        self.branch = base_branch
        self.name = name if name is not None else self._get_name_from_url(self.url)
        self.repo_path = self._get_repo_path(self.dir, self.name)

    def _get_name_from_url(self, url: str) -> str:
        last_slash = url.rfind('/')
        name = url[(last_slash + 1):]
        name = utils.strip_git_suffix(name)
        return name
    
    def _get_repo_path(self, directory: str, name: str) -> str:
        return os.path.join(directory, name)


class RepoManager():
    """Class for managing repos."""

    def __init__(
        self,
        params: str,
    ) -> None:
        """
        Constructor.

        :param params: the parameters container
        """
        self._params = params

    def _clone(
        self,
        info: RepoInfo,
    ) -> Union[Repo, None]:
        """
        Clone a new repo, selecting a specific branch if given.

        :param info: the information of the repo to clone
        :return: the cloned repo object, or `None` if it failed
        """
        print(f"cloning repo '{info.name}' to: {info.repo_path}")
        repo = None
        try:
            # If branch is not specified, we'll use the default branch
            if info.branch is None:
                repo = Repo.clone_from(info.url, info.repo_path)
            else:
                repo = Repo.clone_from(info.url, info.repo_path, branch=info.branch)
            return repo
        except GitError as e:
            raise utils.EmailToPrError('failed to clone repo', e)

    def clone_from_email(
        self,
        msg: EmailMessage,
    ) -> Tuple[Union[Repo, None], Union[RepoInfo, None]]:
        """
        Clone repo corresponding to email and checkout base branch.

        :param msg: the email message
        :return: (repo, repo information) or (`None`, `None`) if email has no URL
        """
        # URL is mandatory
        url = utils.get_repo_url(msg.get_payload())
        if url is None:
            return None, None
        # Insert username and password into URL
        url = utils.insert_token_in_remote_url(
            url,
            self._params.repo_user,
            self._params.repo_token)
        # Base branch is not mandatory
        base_branch = utils.get_base_branch(msg.get_payload())
        info = RepoInfo(self._params.repo_dir, url, base_branch)
        return self._clone(info), info

    def _checkout_new_branch(
        self,
        repo: Repo,
    ) -> Tuple[str, str]:
        """
        Create and checkout new branch from current branch.

        :param repo: the repo object
        :return: (the name of the new branch on which to apply the patch,
            the name of the original/base branch)
        """
        base_branch_name = str(repo.active_branch)
        new_branch_name = f'{base_branch_name}-{time.strftime("%Y%m%d%H%M%S")}'
        print(f"creating new branch '{new_branch_name}' from branch '{base_branch_name}'")
        new_branch = repo.create_head(new_branch_name)
        print('switching to new branch')
        repo.head.reference = new_branch
        return new_branch_name, base_branch_name

    def _apply_patch_file(
        self,
        repo: Repo,
        patch_filename: str,
    ) -> None:
        """
        Apply patch to repo.

        :param repo: the repo
        :param patch_filename: the name of the patch file to apply
        """
        command = f'git am {patch_filename}'
        args = shlex.split(command)
        repo_directory = repo.working_dir
        print(f'previous commit: {repo.head.commit}')
        print(f"applying patch '{patch_filename}'")
        try:
            subprocess.check_output(args, cwd=repo_directory)
            print(f'new commit: {repo.head.commit}')
        except subprocess.CalledProcessError as e:
            raise utils.EmailToPrError('failed to apply patch file', e)

    def apply_patch(
        self,
        repo: Repo,
        patch_filename: str,
    ) -> str:
        """
        Apply patch to repo.

        :param repo: the repo object
        :param patch_filename: the name of the patch file (should be in the repo directory)
        :return: (the name of the branch on which the patch was applied,
            the name of the original/base branch)
        """
        # Create new branch from the current one
        new_branch_name, base_branch_name = self._checkout_new_branch(repo)
        # Apply patch file
        self._apply_patch_file(repo, patch_filename)
        return new_branch_name, base_branch_name

    def push(
        self,
        repo: Repo,
    ) -> None:
        """
        Push current branch to remote.

        :param repo: the repo object
        """
        print('pushing branch to remote')
        try:
            # Use local branch name as upstream branch name
            info_list = repo.remotes.origin.push(refspec=repo.active_branch)
        except GitError as e:
            raise utils.EmailToPrError('failed to push branch to remote', e)


def add_args(parser: argparse.ArgumentParser) -> None:
    """Add repo managing args."""
    parser.add_argument(
        '--repo-dir', '-d',
        help='the directory in which to put the repos (default: %(default)s)',
        default='/tmp/repos')
    parser.add_argument(
        'repo_user',
        help='the username for remote repo authentication')
    parser.add_argument(
        'repo_token',
        help='the token for remote repo authentication')


def parse_args() -> Any:
    """Parse email polling arguments."""
    parser = argparse.ArgumentParser(description='Launch repo manager.')
    add_args(parser)
    return parser.parse_args()


def main() -> None:
    """Entrypoint for testing."""
    args = parse_args()
    manager = RepoManager(args)
    info = RepoInfo(args.repo_dir, 'https://github.com/christophebedard/email2pr.git', 'master')
    repo = manager._clone(info)
    manager.apply_patch(repo, info, 'todo')


if __name__ == '__main__':
    main()
