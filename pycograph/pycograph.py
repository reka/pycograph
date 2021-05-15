"""Main module for Pycograph"""
from redisgraph.graph import Graph  # type: ignore

from pycograph.parse_result_to_redisgraph import populate_graph
from pycograph.project import PythonProject
from pycograph.schemas.pycograph_input import PycographLoadInput


def load(load_input: PycographLoadInput) -> Graph:
    """Load a Python project's code into a graph model.

    :param load_input: An object containing the input data.
    :type load_input: PycographLoadInput
    :return: A RedisGraph graph with the parsed Python project.
    :rtype: Graph
    """
    project = PythonProject(root_dir_path=load_input.project_dir_path)  # type: ignore
    project_parse_result = project.parse()
    return populate_graph(load_input.graph_name, project_parse_result)  # type: ignore
