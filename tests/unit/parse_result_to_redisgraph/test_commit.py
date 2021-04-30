import pytest
import redis.exceptions
from redisgraph.graph import Graph

from pycograph.exceptions import (
    RedisConnectionException,
    RedisResponseException,
    RedisWithoutGraphException,
)
from pycograph.parse_result_to_redisgraph import _commit_graph


def test_connection_error(mocker):
    graph = Graph("test_graph", None)
    mocker.patch.object(graph, "commit", side_effect=redis.exceptions.ConnectionError)

    with pytest.raises(RedisConnectionException):
        _commit_graph(graph)


def test_no_graph_supported(mocker):
    graph = Graph("test_graph", None)
    mocker.patch.object(
        graph,
        "commit",
        side_effect=redis.exceptions.ResponseError(
            "unknown command `GRAPH.QUERY` whatever"
        ),
    )

    with pytest.raises(RedisWithoutGraphException):
        _commit_graph(graph)


def test_unknown_response_error(mocker):
    graph = Graph("test_graph", None)
    mocker.patch.object(
        graph,
        "commit",
        side_effect=redis.exceptions.ResponseError("some unknown error"),
    )

    with pytest.raises(RedisResponseException):
        _commit_graph(graph)
