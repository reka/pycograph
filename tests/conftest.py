import os
from pathlib import Path

import pytest


@pytest.fixture
def test_data_dir():
    test_root_dir = os.path.dirname(__file__)
    project_root_dir = Path(test_root_dir).parent
    return os.path.join(project_root_dir, "test_data")


@pytest.fixture
def no_graph_commit(mocker):
    mocker.patch("redisgraph.graph.Graph.commit")
