import os

from pycograph import pycograph
from pycograph.schemas.parse_result import CONTAINS
from pycograph.schemas.pycograph_input import PycographLoadInput
from tests.integration.whole_projects.helpers import assert_edge, assert_node


def test_mini_project(test_data_dir, no_graph_commit):
    mini_project_path = os.path.join(test_data_dir, "mini-project")

    result = pycograph.load(PycographLoadInput(project_dir_path=mini_project_path))

    assert result.name == "mini-project"
    assert len(result.nodes) == 3
    assert len(result.edges) == 2

    nodes = list(result.nodes.values())

    mini_package_node = assert_node(
        nodes, label="package", name="mini", full_name="mini"
    )

    example_module_node = assert_node(
        nodes, label="module", name="example", full_name="mini.example"
    )

    answer_function_node = assert_node(
        nodes, label="function", name="answer", full_name="mini.example.answer"
    )

    assert_edge(mini_package_node, CONTAINS, example_module_node, result)
    assert_edge(example_module_node, CONTAINS, answer_function_node, result)
