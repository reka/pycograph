"""Exceptions of Pycograph"""


class PycographException(Exception):
    """The base exception class. Specific exception classes should inherit from this."""


class RedisConnectionException(PycographException):
    """Wraps errors connecting to the Redis database."""
