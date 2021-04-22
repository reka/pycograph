"""Main module for Pycograph"""
import os
from typing import Optional

from redisgraph.graph import Graph  # type: ignore

from pycograph.parse_result_to_redisgraph import populate_graph
from pycograph.project import PythonProject


def load(project_dir_path: Optional[str], graph_name: Optional[str] = None) -> Graph:
    """Load a Python project's code into a graph model.

    :param project_dir_path: The path of the Python project.
    :type project_dir_path: Optional[str]
    :param graph_name: the name of the graph, defaults to None
    :type graph_name: Optional[str]
    :return: A RedisGraph graph with the parsed Python project.
    :rtype: Graph
    """
    if not project_dir_path:
        project_dir_path = os.getcwd()
    if not graph_name:
        graph_name = os.path.split(project_dir_path)[-1]
    project = PythonProject(root_dir_path=project_dir_path)
    project_parse_result = project.parse()
    redis_graph = populate_graph(graph_name, project_parse_result)
    return redis_graph
