import pytest

from pycograph.schemas.parse_result import ConstantWithContext, FunctionWithContext
from tests.integration.helper import create_module_with_content


def test_define_a_function_in_production_code():
    content = """
def dummy():
    pass
"""
    modu = create_module_with_content(content)

    modu.parse()

    assert len(modu.contained_objects) == 1
    only_content = modu.contained_objects[0]
    assert type(only_content) == FunctionWithContext
    assert only_content.name == "dummy"
    assert only_content.label() == "function"


def test_define_a_test_function_in_test_module():
    content = """
def test_dummy():
    pass
"""
    modu = create_module_with_content(content, package_name="tests.unit.helpers")

    modu.parse()

    assert len(modu.contained_objects) == 1
    only_content = modu.contained_objects[0]
    assert type(only_content) == FunctionWithContext
    assert only_content.name == "test_dummy"
    assert only_content.label() == "test_function"


def test_define_a_helper_function_in_test_module():
    content = """
def dummy():
    pass
"""
    modu = create_module_with_content(content, package_name="tests.unit.helpers")

    modu.parse()

    assert len(modu.contained_objects) == 1
    only_content = modu.contained_objects[0]
    assert type(only_content) == FunctionWithContext
    assert only_content.name == "dummy"
    assert only_content.label() == "test_helper_function"
