import itertools
import re
from typing import List


def determine_name_parts(name: str) -> List[str]:
    if "_" in name:
        return name.lower().split("_")
    if name != name.lower():
        return split_camel_case(name)
    return [name]


def split_camel_case(camel_name: str) -> List[str]:
    camel_parts = re.findall(r"[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))", camel_name)
    return [cp.lower() for cp in camel_parts]


def determine_full_name_parts(full_name: str) -> List[str]:
    elements = full_name.split(".")
    all_element_parts = [determine_name_parts(e) for e in elements]
    return list(itertools.chain.from_iterable(all_element_parts))
