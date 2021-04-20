from pycograph.schemas.basic_syntax_elements import CallSyntaxElement
from pycograph.schemas.parse_result import (
    CallsRelationship,
    ContainsRelationship,
    ModuleWithContext,
)
import pytest

REFERENCE_OTHER_FUNCTION = """
def do_stuff(nr):
    return nr

def other():
    sample_func = do_stuff
"""


@pytest.mark.parametrize(
    ("content", "module_name", "package_name"),
    [(REFERENCE_OTHER_FUNCTION, "example", "project")],
)
def test_function_call_in_module(project_with_1_module):
    project = project_with_1_module

    project.parse()

    assert len(project.objects) == 3

    module_element = project.objects["project.example"]
    assert type(module_element) == ModuleWithContext
    assert module_element.name == "example"
    assert module_element.full_name == "project.example"

    contains_do_stuff_rel = ContainsRelationship(
        destination_full_name="project.example.do_stuff"
    )
    contains_other_rel = ContainsRelationship(
        destination_full_name="project.example.other"
    )
    assert [contains_do_stuff_rel, contains_other_rel] == module_element.relationships

    other_element = project.objects["project.example.other"]
    calls_do_stuff_rel = CallsRelationship(
        destination_full_name="project.example.do_stuff",
        syntax_element=CallSyntaxElement(what_reference_name="do_stuff"),
    )
    assert other_element.relationships == [calls_do_stuff_rel]


CALLING_CLASS_METHOD = """
class Example():
    def do_stuff(nr):
        return nr

def other():
    sample_func = Example().do_stuff
"""


@pytest.mark.parametrize(
    ("content", "module_name", "package_name"),
    [(CALLING_CLASS_METHOD, "example", "project")],
)
def test_calling_class_method_in_module(project_with_1_module):
    project = project_with_1_module

    project.parse()

    assert len(project.objects) == 4

    module_element = project.objects["project.example"]
    assert type(module_element) == ModuleWithContext
    assert module_element.name == "example"
    assert module_element.full_name == "project.example"

    contains_example_rel = ContainsRelationship(
        destination_full_name="project.example.Example"
    )
    contains_other_rel = ContainsRelationship(
        destination_full_name="project.example.other"
    )
    assert [contains_example_rel, contains_other_rel] == module_element.relationships

    other_element = project.objects["project.example.other"]
    calls_do_stuff_rel = CallsRelationship(
        destination_full_name="project.example.Example.do_stuff",
        syntax_element=CallSyntaxElement(
            what_reference_name="Example", called_attribute="do_stuff"
        ),
    )
    calls_example_rel = CallsRelationship(
        destination_full_name="project.example.Example",
        syntax_element=CallSyntaxElement(what_reference_name="Example"),
    )
    assert other_element.relationships == [calls_do_stuff_rel, calls_example_rel]


CALLING_METHOD_IN_CLASS = """
class Example():
    def do_stuff(self, nr):
        return nr

    def other(self):
        nr = self.do_stuff()
"""


@pytest.mark.parametrize(
    ("content", "module_name", "package_name"),
    [(CALLING_METHOD_IN_CLASS, "example", "project")],
)
def test_calling_method_in_class(project_with_1_module):
    project = project_with_1_module

    project.parse()

    assert len(project.objects) == 4

    module_element = project.objects["project.example"]
    assert type(module_element) == ModuleWithContext
    assert module_element.name == "example"
    assert module_element.full_name == "project.example"

    contains_example_rel = ContainsRelationship(
        destination_full_name="project.example.Example"
    )
    assert [contains_example_rel] == module_element.relationships

    contains_do_stuff_rel = ContainsRelationship(
        destination_full_name="project.example.Example.do_stuff"
    )
    contains_other_rel = ContainsRelationship(
        destination_full_name="project.example.Example.other"
    )
    example_class_element = project.objects["project.example.Example"]
    assert [
        contains_do_stuff_rel,
        contains_other_rel,
    ] == example_class_element.relationships

    other_element = project.objects["project.example.Example.other"]
    calls_do_stuff_rel = CallsRelationship(
        destination_full_name="project.example.Example.do_stuff",
        syntax_element=CallSyntaxElement(
            what_reference_name="self", called_attribute="do_stuff"
        ),
    )
    calls_example_rel = CallsRelationship(
        destination_full_name="project.example.Example",
        syntax_element=CallSyntaxElement(what_reference_name="self"),
    )
    assert other_element.relationships == [calls_do_stuff_rel, calls_example_rel]
