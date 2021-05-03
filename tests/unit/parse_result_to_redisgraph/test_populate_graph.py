import pytest
import redis
import redis.exceptions

from pycograph.config import settings
from pycograph.exceptions import RedisConnectionException
from pycograph.parse_result_to_redisgraph import populate_graph
from pycograph.schemas.parse_result import ParseResult


def test_delete_graph_connection_error(mocker):
    settings.overwrite_existing_graph = True
    mocker.patch.object(
        redis.Redis, "delete", side_effect=redis.exceptions.ConnectionError
    )

    with pytest.raises(RedisConnectionException):
        populate_graph("dummy", ParseResult(objects=[]))
