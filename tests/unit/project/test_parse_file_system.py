import os
import tempfile

import pytest

from pycograph.exceptions import NoPythonFileFoundException
from pycograph.project import PythonProject


def test_project_dir_empty():
    with tempfile.TemporaryDirectory() as tmpdirname:
        project = PythonProject(tmpdirname)
        with pytest.raises(NoPythonFileFoundException):
            project._parse_file_system()


def test_no_python_file_in_project_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        file_path = os.path.join(tmpdirname, "test.txt")
        with open(file_path, "w") as f:
            f.write("test content")
        project = PythonProject(tmpdirname)
        with pytest.raises(NoPythonFileFoundException):
            project._parse_file_system()
