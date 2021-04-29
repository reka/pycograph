import os
import tempfile

import pytest
from redisgraph.graph import Graph

from pycograph.exceptions import NoPythonFileFoundException
from pycograph.pycograph import load
from pycograph.schemas.pycograph_input import PycographLoadInput


def test_happy_path(test_data_dir, no_graph_commit):
    mini_project_path = os.path.join(test_data_dir, "mini-project")
    load_input = PycographLoadInput(project_dir_path=mini_project_path)

    result = load(load_input)

    assert type(result) == Graph
    assert result.name == "mini-project"


def test_happy_path_with_graph_name(test_data_dir, no_graph_commit):
    mini_project_path = os.path.join(test_data_dir, "mini-project")
    load_input = PycographLoadInput(
        project_dir_path=mini_project_path, graph_name="test-graph"
    )

    result = load(load_input)

    assert type(result) == Graph
    assert result.name == "test-graph"


def test_no_python_file_in_project_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        load_input = PycographLoadInput(
            project_dir_path=tmpdirname, graph_name="test-graph"
        )
        with pytest.raises(NoPythonFileFoundException):
            load(load_input)
