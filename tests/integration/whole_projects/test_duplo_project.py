import os

from pycograph import pycograph


def test_duplo_project(test_data_dir, no_graph_commit):
    duplo_project_path = os.path.join(test_data_dir, "duplo-project")

    result = pycograph.load(duplo_project_path)

    assert result.name == "duplo-project"
    assert len(result.nodes) == 8
    # assert len(result.edges) == 14

    nodes = list(result.nodes.values())

    duplo_package_node = nodes[0]
    assert duplo_package_node.label == "package"
    assert duplo_package_node.properties == {
        "name": "duplo",
        "full_name": "duplo",
        "is_test_object": False,
    }

    content_module_node = nodes[1]
    assert content_module_node.label == "module"
    assert content_module_node.properties == {
        "name": "content",
        "full_name": "duplo.content",
        "is_test_object": False,
    }

    main_module_node = nodes[2]
    assert main_module_node.label == "module"
    assert main_module_node.properties == {
        "name": "main",
        "full_name": "duplo.main",
        "is_test_object": False,
    }

    answer_constant_node = nodes[3]
    assert answer_constant_node.label == "constant"
    assert answer_constant_node.properties == {
        "name": "ANSWER",
        "full_name": "duplo.content.ANSWER",
        "is_test_object": False,
    }

    publ_function_node = nodes[4]
    assert publ_function_node.label == "function"
    assert publ_function_node.properties == {
        "name": "publ",
        "full_name": "duplo.content.publ",
        "is_test_object": False,
    }

    priv_function_node = nodes[5]
    assert priv_function_node.label == "function"
    assert priv_function_node.properties == {
        "name": "priv",
        "full_name": "duplo.content.priv",
        "is_test_object": False,
    }

    dummy_class_node = nodes[6]
    assert dummy_class_node.label == "class"
    assert dummy_class_node.properties == {
        "name": "Dummy",
        "full_name": "duplo.content.Dummy",
        "is_test_object": False,
    }

    bla_function_node = nodes[7]
    assert bla_function_node.label == "function"
    assert bla_function_node.properties == {
        "name": "bla",
        "full_name": "duplo.main.bla",
        "is_test_object": False,
    }

    assert_contains_edge(duplo_package_node, content_module_node, result, 0)
    assert_contains_edge(duplo_package_node, main_module_node, result, 1)

    assert_contains_edge(content_module_node, answer_constant_node, result, 2)
    assert_contains_edge(content_module_node, publ_function_node, result, 3)
    assert_contains_edge(content_module_node, priv_function_node, result, 4)
    assert_contains_edge(content_module_node, dummy_class_node, result, 5)

    assert_contains_edge(main_module_node, bla_function_node, result, 6)

    assert_imports_edge(main_module_node, answer_constant_node, result, 7)
    assert_imports_edge(main_module_node, dummy_class_node, result, 8)
    assert_imports_edge(main_module_node, publ_function_node, result, 9)

    # function call within module
    assert_calls_edge(publ_function_node, priv_function_node, result, 10)

    # calling imported objects
    assert_calls_edge(bla_function_node, answer_constant_node, result, 11)
    assert_calls_edge(bla_function_node, dummy_class_node, result, 12)
    assert_calls_edge(bla_function_node, publ_function_node, result, 13)


def assert_contains_edge(src_node, dest_node, result, edge_index):
    contains_edge = result.edges[edge_index]
    assert contains_edge.relation == "contains"
    assert contains_edge.src_node == src_node
    assert contains_edge.dest_node == dest_node


def assert_imports_edge(src_node, dest_node, result, edge_index):
    imports_edge = result.edges[edge_index]
    assert imports_edge.relation == "imports"
    assert imports_edge.src_node == src_node
    assert imports_edge.dest_node == dest_node


def assert_calls_edge(src_node, dest_node, result, edge_index):
    calls_edge = result.edges[edge_index]
    assert calls_edge.relation == "calls"
    assert calls_edge.src_node == src_node
    assert calls_edge.dest_node == dest_node
