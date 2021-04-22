"""Generate RedisGraph nodes and edges from a ParseResult"""

from typing import Dict

import redis  # type: ignore
from redisgraph import Edge, Graph, Node  # type: ignore

from pycograph.config import settings
from pycograph.exceptions import (
    RedisConnectionException,
    RedisResponseException,
    RedisWithoutGraphException,
)
from pycograph.schemas.parse_result import (
    ParseResult,
    Relationship,
    ObjectWithContext,
)


def populate_graph(graph_name: str, parse_result: ParseResult) -> Graph:
    """Create and commit a RedisGraph `Graph` based on the `ParseResult`.

    :param graph_name: The name of the created graph.
    :type graph_name: str
    :param parse_result: A parsed Python project with objects representing the nodes of the graph.
    :type parse_result: ParseResult
    :raises RedisConnectionException: [description]
    :return: [description]
    :rtype: Graph
    """
    redis_instance = redis.Redis(host=settings.redis_host, port=settings.redis_port)
    if settings.overwrite_existing_graph:
        try:
            redis_instance.delete(graph_name)
        except redis.exceptions.ConnectionError as e:
            raise RedisConnectionException(
                "Could not connect to the Redis instance at the step overwrite."
            ) from e
    redis_graph = Graph(graph_name, redis_instance)
    nodes = {}
    for obj in parse_result.objects.values():
        node = _add_node_to_graph(obj, redis_graph)
        nodes[obj.full_name] = node

    for obj in parse_result.objects.values():
        for rel in obj.relationships:
            _add_edge_to_graph(obj.full_name, rel, nodes, redis_graph)

    _commit_graph(redis_graph)

    return redis_graph


def _commit_graph(redis_graph: Graph) -> None:
    """Commit a `Graph` and handle various errors that can occur.

    :param redis_graph: The graph to be committed.
    :type redis_graph: Graph
    :raises RedisConnectionException: If we can't connect to a Redis instance.
    :raises RedisWithoutGraphException: If the Redis instance doesn't support the GRAPH command.
    :raises RedisResponseException: If the Redis library threw an unclassified ResponseError.
    """
    try:
        redis_graph.commit()
    except redis.exceptions.ConnectionError as e:
        raise RedisConnectionException(
            "Could not connect to the Redis instance at the step commit."
        ) from e
    except redis.exceptions.ResponseError as e:
        if str(e).startswith("unknown command `GRAPH.QUERY`"):
            raise RedisWithoutGraphException(
                "You're connected to a Redis instance, which doesn't support GRAPH commands."
            ) from e
        else:
            raise RedisResponseException from e


def _add_node_to_graph(obj: ObjectWithContext, graph: Graph) -> Node:
    """Add a node to a `Graph` from an object.

    :param obj: The object to be added as a node.
    :type obj: ObjectWithContext
    :param graph: The graph to which we add the node.
    :type graph: Graph
    :return: The new node.
    :rtype: Node
    """
    thing_node = Node(
        label=obj.label(),
        properties=obj.node_properties(),
    )
    graph.add_node(thing_node)
    return thing_node


def _add_edge_to_graph(
    source_full_name: str,
    relationship: Relationship,
    nodes: Dict[str, Node],
    graph: Graph,
) -> None:
    """Create an edge based on a `Relationship` object.

    :param source_full_name: The unique full name of the source node.
    :type source_full_name: str
    :param relationship: The relationship object.
    :type relationship: Relationship
    :param nodes: A dictionary with the nodes and their full names.
    :type nodes: Dict[str, Node]
    :param graph: The graph where we add the edge.
    :type graph: Graph
    """
    node1 = nodes.get(source_full_name)
    node2 = nodes.get(relationship.destination_full_name)
    if node1 and node2:
        edge = Edge(
            node1, relationship.name, node2, properties=relationship.properties()
        )
        graph.add_edge(edge)
