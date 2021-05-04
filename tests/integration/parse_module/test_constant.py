import pytest

from pycograph.schemas.parse_result import ConstantWithContext
from tests.integration.helper import create_module_with_content


@pytest.mark.parametrize("content", ["ANSWER=42"])
def test_define_a_constant(module_with_content):
    modu = module_with_content

    modu.parse()

    assert len(modu.contained_objects) == 1
    only_content = modu.contained_objects[0]
    assert type(only_content) == ConstantWithContext
    assert only_content.name == "ANSWER"
    assert only_content.label() == "constant"


def test_define_a_constant_in_test_module():
    modu = create_module_with_content("ANSWER=42", package_name="tests.unit.helpers")

    modu.parse()

    assert len(modu.contained_objects) == 1
    only_content = modu.contained_objects[0]
    assert type(only_content) == ConstantWithContext
    assert only_content.name == "ANSWER"
    assert only_content.label() == "test_constant"
