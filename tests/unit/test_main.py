import os

import pytest
from redisgraph.graph import Graph

from pycograph.pycograph import load
from pycograph.exceptions import InvalidProjectDirPathException


def test_happy_path(test_data_dir, no_graph_commit):
    mini_project_path = os.path.join(test_data_dir, "mini-project")

    result = load(mini_project_path)

    assert type(result) == Graph
    assert result.name == "mini-project"


def test_happy_path_with_graph_name(test_data_dir, no_graph_commit):
    mini_project_path = os.path.join(test_data_dir, "mini-project")

    result = load(mini_project_path, "test-graph")

    assert type(result) == Graph
    assert result.name == "test-graph"


def test_invalid_project_dir_path():
    with pytest.raises(InvalidProjectDirPathException):
        load("a_non_existing_dir_path", None)
