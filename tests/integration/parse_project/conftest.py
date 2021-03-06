import pytest

from pycograph.project import PythonProject
from tests.integration.helper import create_module_with_content


@pytest.fixture
def project_with_1_module(content, mocker, module_name, package_name):
    modu = create_module_with_content(content, module_name, package_name)
    project = PythonProject(root_dir_path="dummy")

    # Add the module explicitly instead of parsing the file system
    project._add_module(modu)
    mocker.patch("pycograph.project.PythonProject._parse_file_system")

    return project
