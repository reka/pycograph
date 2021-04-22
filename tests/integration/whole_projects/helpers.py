from typing import List

from redisgraph.node import Node


def find_node_with_full_name(full_name: str, nodes: List[Node]):
    nodes_with_name = list(
        filter(lambda n: n.properties["full_name"] == full_name, nodes)
    )
    assert len(nodes_with_name) == 1
    return nodes_with_name[0]


def assert_edge(src_node, relationship, dest_node, result):
    filtered_edges = list(
        filter(
            lambda e: e.relation == relationship
            and e.src_node == src_node
            and e.dest_node == dest_node,
            result.edges,
        )
    )
    assert len(filtered_edges) == 1
