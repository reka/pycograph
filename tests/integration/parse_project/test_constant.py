import pytest

from pycograph.schemas.parse_result import (
    ContainsRelationship,
    ConstantWithContext,
    ModuleWithContext,
)


@pytest.mark.parametrize(
    ("content", "module_name", "package_name"), [("ANSWER=42", "example", "package")]
)
def test_define_a_constant(project_with_1_module):
    project = project_with_1_module

    project.parse()

    assert len(project.objects) == 2
    module_element = project.objects["package.example"]
    assert type(module_element) == ModuleWithContext
    assert module_element.name == "example"
    assert module_element.full_name == "package.example"

    contains_rel = ContainsRelationship(destination_full_name="package.example.ANSWER")
    assert [contains_rel] == module_element.relationships

    constant_element = project.objects["package.example.ANSWER"]
    assert type(constant_element) == ConstantWithContext
    assert constant_element.name == "ANSWER"
