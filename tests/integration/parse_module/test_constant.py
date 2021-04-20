import pytest

from pycograph.schemas.parse_result import ConstantWithContext


@pytest.mark.parametrize("content", ["ANSWER=42"])
def test_define_a_constant(module_with_content):
    modu = module_with_content

    modu.parse()

    assert len(modu.contained_objects) == 1
    only_content = modu.contained_objects[0]
    assert type(only_content) == ConstantWithContext
    assert only_content.name == "ANSWER"
