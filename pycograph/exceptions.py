"""Exceptions of Pycograph"""


class PycographException(Exception):
    """The base exception class. Specific exception classes should inherit from this."""


class RedisConnectionException(PycographException):
    """Wraps errors connecting to the Redis database."""


class RedisResponseException(PycographException):
    """Wraps unclassified ResponseError from a the RedisGraph client library."""


class RedisWithoutGraphException(PycographException):
    """Connecting to a RedisInstance without the RedisGraph module."""


class ModuleWithInvalidContentException(PycographException):
    """A module containing invalid syntax."""
