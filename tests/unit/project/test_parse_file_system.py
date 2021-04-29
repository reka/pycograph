import tempfile

import pytest

from pycograph.exceptions import NoPythonFileFoundException
from pycograph.project import PythonProject


def test_no_python_file_in_project_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        project = PythonProject(tmpdirname)
        with pytest.raises(NoPythonFileFoundException):
            project._parse_file_system()
