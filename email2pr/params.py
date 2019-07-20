"""Module for parameter file wrapper and parsing."""

import yaml
from typing import Union

from . import utils


class Params():
    """Parameters wrappers."""

    def __init__(
        self,
        filename: str,
    ) -> None:
        """
        Constructor.

        :param filename: the name of the parameters file to parse
        """
        self.params = {}
        self._parse_params_file(filename)

    def _parse_params_file(self, filename: str) -> None:
        """
        Parse parameters files and create params dict.

        :param filename: the name of the file to parse
        """
        content = open(filename, 'r').read()
        for data in yaml.load_all(content):
            self.params = {**self.params, **data}
        print(f'parameters: {self.params}')

    def __getattr__(self, name) -> Union[str, None]:
        if self.params is None:
            raise utils.EmailToPrError('parameters file has not been parsed')
        return self.params.get(name, None)


if __name__ == '__main__':
    p = Params('params.yaml')
