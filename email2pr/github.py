"""Module for interfacing with GitHub."""

import argparse

from github import Github


class PrInfo():
    """Information to create a pull request."""

    def __init__(
        self,
        user_org: str,
        repo_name: str,
        branch_base: str,
        branch_head: str,
        title: str,
        body: str,
        user_org_origin: str = None,
    ) -> None:
        """
        Constructor.

        :param user_org: the username or the organisation of the repo on which to open the PR
        :param repo_name: the name of the repo on which to open the pull request
        :param branch_base: the name of the base branch which is the target of this PR
        :param branch_head: the name of the branch which we want to merge into the base branch
        :param title: the title of the pull request
        :param body: the body of the pull request
        :param user_org_origin: the username or organisation name that contains the PR branch, or 
            `None` if it's the same as user_org
        """
        self.user_org = user_org
        self.repo_name = repo_name
        self.branch_base = branch_base
        # TODO might be from a different repo
        self.branch_head = branch_head
        self.title = title
        self.body = body
        self.user_org_origin = user_org_origin if user_org_origin is not None else user_org

    @property
    def full_pr_repo(self) -> str:
        return f'{self.user_org}/{self.repo_name}'


def create_pr(
    token: str,
    info: PrInfo,
) -> str:
    """
    Create pull request.

    :param token: the token to access the GitHub API
    :param info: the pull request info
    :return: the pull request URL
    """
    g = Github(token)
    repo = g.get_repo(info.full_pr_repo)
    pr = repo.create_pull(
        title=info.title,
        head=info.branch_head,
        base=info.branch_base,
        body=info.body,
    )
    return pr.url


def add_args(parser: argparse.ArgumentParser) -> None:
    """Add github args."""
    parser.add_argument(
        'github_token',
        help='the token to use to access the GitHub API')
