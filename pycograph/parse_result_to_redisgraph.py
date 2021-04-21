"""Generate RedisGraph nodes and edges from a ParseResult"""

import redis  # type: ignore
from redis.exceptions import ConnectionError
from redisgraph import Edge, Graph, Node  # type: ignore

from pycograph.config import settings
from pycograph.exceptions import RedisConnectionException
from pycograph.schemas.parse_result import (
    ParseResult,
    Relationship,
    ObjectWithContext,
)


def populate_graph(graph_name: str, result: ParseResult) -> Graph:
    redis_instance = redis.Redis(host=settings.redis_host, port=settings.redis_port)
    if settings.overwrite_existing_graph:
        try:
            redis_instance.delete(graph_name)
        except ConnectionError as e:
            raise RedisConnectionException(
                "Could not connect to the Redis instance at the step overwrite."
            ) from e
    redis_graph = Graph(graph_name, redis_instance)
    nodes = {}
    for thing in result.objects.values():
        node = add_to_graph(thing, redis_graph)
        nodes[thing.full_name] = node

    for thing in result.objects.values():
        for rel in thing.relationships:
            add_edge_to_graph(thing.full_name, rel, nodes, redis_graph)

    try:
        redis_graph.commit()
    except ConnectionError as e:
        raise RedisConnectionException(
            "Could not connect to the Redis instance at the step commit."
        ) from e

    return redis_graph


def add_to_graph(thing: ObjectWithContext, graph: Graph) -> Node:
    thing_node = Node(
        label=thing.label(),
        properties=thing.node_properties(),
    )
    graph.add_node(thing_node)
    return thing_node


def add_edge_to_graph(
    source_full_name: str, relationship: Relationship, nodes: dict, graph: Graph
) -> None:
    node1 = nodes.get(source_full_name)
    node2 = nodes.get(relationship.destination_full_name)
    if node1 and node2:
        edge = Edge(
            node1, relationship.name, node2, properties=relationship.properties()
        )
        graph.add_edge(edge)
