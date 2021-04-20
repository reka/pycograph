import os

from pycograph import pycograph


def test_mini_project(test_data_dir, no_graph_commit):
    mini_project_path = os.path.join(test_data_dir, "mini-project")

    result = pycograph.load(mini_project_path)

    assert result.name == "mini-project"
    assert len(result.nodes) == 3
    assert len(result.edges) == 2

    nodes = list(result.nodes.values())

    mini_package_node = nodes[0]
    assert mini_package_node.label == "package"
    assert mini_package_node.properties == {
        "name": "mini",
        "full_name": "mini",
        "is_test_object": False,
    }

    example_module_node = nodes[1]
    assert example_module_node.label == "module"
    assert example_module_node.properties == {
        "name": "example",
        "full_name": "mini.example",
        "is_test_object": False,
    }

    answer_function_node = nodes[2]
    assert answer_function_node.label == "function"
    assert answer_function_node.properties == {
        "name": "answer",
        "full_name": "mini.example.answer",
        "is_test_object": False,
    }

    package_contains_module_edge = result.edges[0]
    assert package_contains_module_edge.relation == "contains"
    assert package_contains_module_edge.src_node == mini_package_node
    assert package_contains_module_edge.dest_node == example_module_node

    module_contains_function_edge = result.edges[1]
    assert module_contains_function_edge.relation == "contains"
    assert module_contains_function_edge.src_node == example_module_node
    assert module_contains_function_edge.dest_node == answer_function_node
