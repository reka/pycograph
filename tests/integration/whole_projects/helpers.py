from typing import List

from redisgraph.node import Node


def find_node_with_full_name(full_name: str, nodes: List[Node]):
    nodes_with_name = list(
        filter(lambda n: n.properties["full_name"] == full_name, nodes)
    )
    assert len(nodes_with_name) == 1
    return nodes_with_name[0]
