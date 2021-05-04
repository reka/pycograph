from pycograph.schemas.parse_result import ClassWithContext, ConstantWithContext
from tests.integration.helper import create_module_with_content


def test_define_a_class_in_production_code():
    content = """
class Dummy:
    pass
"""
    modu = create_module_with_content(content)

    modu.parse()

    assert len(modu.contained_objects) == 1
    only_content = modu.contained_objects[0]
    assert type(only_content) == ClassWithContext
    assert only_content.name == "Dummy"
    assert only_content.label() == "class"


def test_define_a_class_in_test_module():
    content = """
class Dummy:
    pass
"""
    modu = create_module_with_content(content, package_name="tests.unit.helpers")

    modu.parse()

    assert len(modu.contained_objects) == 1
    only_content = modu.contained_objects[0]
    assert type(only_content) == ClassWithContext
    assert only_content.name == "Dummy"
    assert only_content.label() == "test_class"
