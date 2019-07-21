"""Module for parameter file wrapper and parsing."""

import yaml
from typing import List
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
    
    def _assert_file_parsed(self) -> None:
        """Assert that the parameters file has been parsed."""
        if self.params is None:
            raise utils.EmailToPrError('parameters file has not been parsed')

    def __getattr__(self, name) -> Union[str, None]:
        self._assert_file_parsed()
        return self.params.get(name, None)

    def assert_params_defined(self, parameters: List[str]) -> None:
        """
        Assert that a list of parameters are defined.

        :param parameters: the list of parameters names to check
        """
        self._assert_file_parsed()
        undefined_params = []
        for param in parameters:
            if self.params.get(param, None) is None:
                undefined_params.append(param)
        if len(undefined_params) > 0:
            raise utils.EmailToPrError(f'parameter(s) not defined: {undefined_params}')


if __name__ == '__main__':
    p = Params('params.yaml')
