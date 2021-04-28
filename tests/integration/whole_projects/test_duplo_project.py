import os

from pycograph import pycograph
from pycograph.schemas.pycograph_input import PycographLoadInput
from pycograph.schemas.parse_result import CALLS, CONTAINS, IMPORTS
from tests.integration.whole_projects.helpers import (
    assert_edge,
    find_node_with_full_name,
)


def test_duplo_project(test_data_dir, no_graph_commit):
    duplo_project_path = os.path.join(test_data_dir, "duplo-project")

    result = pycograph.load(PycographLoadInput(project_dir_path=duplo_project_path))

    assert result.name == "duplo-project"
    assert len(result.nodes) == 8
    assert len(result.edges) == 14

    nodes = list(result.nodes.values())

    duplo_package_node = find_node_with_full_name("duplo", nodes)
    assert duplo_package_node.label == "package"
    assert duplo_package_node.properties == {
        "name": "duplo",
        "full_name": "duplo",
        "is_test_object": False,
    }

    content_module_node = find_node_with_full_name("duplo.content", nodes)
    assert content_module_node.label == "module"
    assert content_module_node.properties == {
        "name": "content",
        "full_name": "duplo.content",
        "is_test_object": False,
    }

    main_module_node = find_node_with_full_name("duplo.main", nodes)
    assert main_module_node.label == "module"
    assert main_module_node.properties == {
        "name": "main",
        "full_name": "duplo.main",
        "is_test_object": False,
    }

    answer_constant_node = find_node_with_full_name("duplo.content.ANSWER", nodes)
    assert answer_constant_node.label == "constant"
    assert answer_constant_node.properties == {
        "name": "ANSWER",
        "full_name": "duplo.content.ANSWER",
        "is_test_object": False,
    }

    publ_function_node = find_node_with_full_name("duplo.content.publ", nodes)
    assert publ_function_node.label == "function"
    assert publ_function_node.properties == {
        "name": "publ",
        "full_name": "duplo.content.publ",
        "is_test_object": False,
    }

    priv_function_node = find_node_with_full_name("duplo.content.priv", nodes)
    assert priv_function_node.label == "function"
    assert priv_function_node.properties == {
        "name": "priv",
        "full_name": "duplo.content.priv",
        "is_test_object": False,
    }

    dummy_class_node = find_node_with_full_name("duplo.content.Dummy", nodes)
    assert dummy_class_node.label == "class"
    assert dummy_class_node.properties == {
        "name": "Dummy",
        "full_name": "duplo.content.Dummy",
        "is_test_object": False,
    }

    bla_function_node = find_node_with_full_name("duplo.main.bla", nodes)
    assert bla_function_node.label == "function"
    assert bla_function_node.properties == {
        "name": "bla",
        "full_name": "duplo.main.bla",
        "is_test_object": False,
    }

    assert_edge(duplo_package_node, CONTAINS, content_module_node, result)
    assert_edge(duplo_package_node, CONTAINS, main_module_node, result)

    assert_edge(content_module_node, CONTAINS, answer_constant_node, result)
    assert_edge(content_module_node, CONTAINS, publ_function_node, result)
    assert_edge(content_module_node, CONTAINS, priv_function_node, result)
    assert_edge(content_module_node, CONTAINS, dummy_class_node, result)

    assert_edge(main_module_node, CONTAINS, bla_function_node, result)

    assert_edge(main_module_node, IMPORTS, answer_constant_node, result)
    assert_edge(main_module_node, IMPORTS, dummy_class_node, result)
    assert_edge(main_module_node, IMPORTS, publ_function_node, result)

    # function call within module
    assert_edge(publ_function_node, CALLS, priv_function_node, result)

    # calling imported objects
    assert_edge(bla_function_node, CALLS, answer_constant_node, result)
    assert_edge(bla_function_node, CALLS, dummy_class_node, result)
    assert_edge(bla_function_node, CALLS, publ_function_node, result)
