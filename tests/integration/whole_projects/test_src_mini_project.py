import os

from pycograph import pycograph
from pycograph.schemas.parse_result import CONTAINS
from pycograph.schemas.pycograph_input import PycographLoadInput
from tests.integration.whole_projects.helpers import (
    assert_edge,
    find_node_with_full_name,
)


def test_mini_project(test_data_dir, no_graph_commit):
    mini_project_path = os.path.join(test_data_dir, "src-mini-project")

    result = pycograph.load(PycographLoadInput(project_dir_path=mini_project_path))

    assert result.name == "src-mini-project"
    assert len(result.nodes) == 3
    assert len(result.edges) == 2

    nodes = list(result.nodes.values())

    mini_package_node = find_node_with_full_name("mini", nodes)
    assert mini_package_node.label == "package"
    assert mini_package_node.properties == {
        "name": "mini",
        "full_name": "mini",
        "is_test_object": False,
    }

    example_module_node = find_node_with_full_name("mini.example", nodes)
    assert example_module_node.label == "module"
    assert example_module_node.properties == {
        "name": "example",
        "full_name": "mini.example",
        "is_test_object": False,
    }

    answer_function_node = find_node_with_full_name("mini.example.answer", nodes)
    assert answer_function_node.label == "function"
    assert answer_function_node.properties == {
        "name": "answer",
        "full_name": "mini.example.answer",
        "is_test_object": False,
    }

    assert_edge(mini_package_node, CONTAINS, example_module_node, result)
    assert_edge(example_module_node, CONTAINS, answer_function_node, result)
