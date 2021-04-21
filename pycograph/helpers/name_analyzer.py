"""Helper functions to analyze the names of objects."""

import itertools
import re
from typing import List


def determine_name_parts(name: str) -> List[str]:
    """Split a name into parts: supported formats: snake case, camel case.

    :param name: The name to split.
    :type name: str
    :return: The parts of the name.
    :rtype: List[str]
    """
    if "_" in name:
        return name.lower().split("_")
    if name != name.lower():
        return split_camel_case(name)
    return [name]


def split_camel_case(camel_name: str) -> List[str]:
    """Split a camel case name into parts.

    :param camel_name: A name in camel case.
    :type camel_name: str
    :return: The parts of the name.
    :rtype: List[str]
    """
    camel_parts = re.findall(r"[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))", camel_name)
    return [cp.lower() for cp in camel_parts]


def determine_full_name_parts(full_name: str) -> List[str]:
    """Split all parts of a fully qualified name.

    It's possible that a part of the name is camel case, another part in snake case.
    E.g. project.sample_pkg.MainExample

    :param full_name: The fully qualified name of a Python object.
    :type full_name: str
    :return: The parts of the parts.
    :rtype: List[str]
    """
    elements = full_name.split(".")
    all_element_parts = [determine_name_parts(e) for e in elements]
    return list(itertools.chain.from_iterable(all_element_parts))
