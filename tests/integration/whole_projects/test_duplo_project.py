import os

from pycograph import pycograph
from pycograph.schemas.parse_result import CALLS, CONTAINS, IMPORTS
from pycograph.schemas.pycograph_input import PycographLoadInput
from tests.integration.whole_projects.helpers import assert_edge, assert_node


def test_duplo_project(test_data_dir, no_graph_commit):
    duplo_project_path = os.path.join(test_data_dir, "duplo-project")

    result = pycograph.load(PycographLoadInput(project_dir_path=duplo_project_path))

    assert result.name == "duplo-project"
    assert len(result.nodes) == 8
    assert len(result.edges) == 14

    nodes = list(result.nodes.values())

    duplo_package_node = assert_node(
        nodes, label="package", name="duplo", full_name="duplo"
    )

    content_module_node = assert_node(
        nodes,
        label="module",
        name="content",
        full_name="duplo.content",
    )

    main_module_node = assert_node(
        nodes,
        label="module",
        name="main",
        full_name="duplo.main",
    )

    answer_constant_node = assert_node(
        nodes,
        label="constant",
        name="ANSWER",
        full_name="duplo.content.ANSWER",
    )

    publ_function_node = assert_node(
        nodes,
        label="function",
        name="publ",
        full_name="duplo.content.publ",
    )

    priv_function_node = assert_node(
        nodes,
        label="function",
        name="priv",
        full_name="duplo.content.priv",
    )

    dummy_class_node = assert_node(
        nodes,
        label="class",
        name="Dummy",
        full_name="duplo.content.Dummy",
    )

    bla_function_node = assert_node(
        nodes,
        label="function",
        name="bla",
        full_name="duplo.main.bla",
    )

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
