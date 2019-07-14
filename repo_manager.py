#!/usr/bin/env python3
"""Module for dealing with git repos."""

from git import Repo
import os
from typing import Union


class RepoInfo():
    """Repo information container."""

    def __init__(
        self,
        url: str,
        name: str = None,
    ) -> None:
        """
        Constructor.

        :param name: the name to use as a reference
        :param url: the origin remote URL for the repo
        """
        self.url = url
        if name is None:
            name = self._get_name_from_url(self.url)
        self.name = name
    
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

    def clone(self, url: str) -> None:
        """Clone a new repo."""
        info = RepoInfo(url)
        path = os.path.join(self._repo_dir, info.name)
        print(f"cloning repo '{info.name}' to: {path}")
        repo = Repo.clone_from(info.url, path)

    def get_key_value(self, body: str, key: str) -> Union[str, None]:
        """
        Extract value for a given key.

        :param body: the body in which to search
        :param key: the key to look for
        :return: the URL value, or `None` if not found
        """
        url = None
        for line in body.splitlines():
            if line.startswith(key):
                sep_index = line.find(':')
                url = line[(sep_index + 1):].strip()
        return url

    def get_repo_url(self, body: str) -> Union[str, None]:
        """
        Extract repo URL value from body.

        :param body: the body in which to search
        :return: the URL value, or `None` if not found
        """
        get_key_value(body, 'Github-Repo-Url:')


def main():
    """Entrypoint for testing."""
    manager = RepoManager('/tmp/repos')
    manager.clone('https://github.com/christophebedard/email2pr.git')


if __name__ == '__main__':
    main()
