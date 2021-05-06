from pycograph.project import PythonProject
from pycograph.schemas.basic_syntax_elements import CallSyntaxElement
from pycograph.schemas.parse_result import CallsRelationship

from ..helper import create_module_with_content


def test_import_from_and_call():
    content = """
def do_stuff(nr):
    return nr
"""
    logic_module = create_module_with_content(content, "logic", "package")

    importer_content = """
from package.logic import do_stuff

def other():
    do_stuff()
"""
    importer_module = create_module_with_content(
        importer_content,
        "importer",
        "package",
    )

    project = PythonProject(root_dir_path="dummy")
    project._add_module(logic_module)
    project._add_module(importer_module)

    project.parse()

    assert len(project.objects) == 4

    other_function_object = project.objects["package.importer.other"]
    calls_do_stuff_rel = CallsRelationship(
        destination_full_name="package.logic.do_stuff",
        syntax_element=CallSyntaxElement(what_reference_name="do_stuff"),
    )
    assert other_function_object.relationships == [calls_do_stuff_rel]


def test_import_from_as_and_call():
    content = """
def do_stuff(nr):
    return nr
"""
    logic_module = create_module_with_content(content, "logic", "package")

    importer_content = """
from package.logic import do_stuff as sth_else

def other():
    sth_else()
"""
    importer_module = create_module_with_content(
        importer_content,
        "importer",
        "package",
    )

    project = PythonProject(root_dir_path="dummy")
    project._add_module(logic_module)
    project._add_module(importer_module)

    project.parse()

    assert len(project.objects) == 4

    other_function_object = project.objects["package.importer.other"]
    calls_do_stuff_rel = CallsRelationship(
        destination_full_name="package.logic.do_stuff",
        syntax_element=CallSyntaxElement(what_reference_name="sth_else"),
    )
    assert other_function_object.relationships == [calls_do_stuff_rel]


def test_import_imported_name_and_call():
    content = """
def do_stuff(nr):
    return nr
"""
    logic_module = create_module_with_content(content, "logic", "package")

    first_importer_content = """
from package.logic import do_stuff
"""
    first_importer_module = create_module_with_content(
        first_importer_content,
        "first_importer",
        "package",
    )

    second_importer_content = """
from package.first_importer import do_stuff

def other():
    do_stuff()
"""

    second_importer_module = create_module_with_content(
        second_importer_content,
        "second_importer",
        "package",
    )

    project = PythonProject(root_dir_path="dummy")
    project._add_module(logic_module)
    project._add_module(first_importer_module)
    project._add_module(second_importer_module)

    project.parse()

    assert len(project.objects) == 5

    other_function_object = project.objects["package.second_importer.other"]
    calls_do_stuff_rel = CallsRelationship(
        destination_full_name="package.logic.do_stuff",
        syntax_element=CallSyntaxElement(what_reference_name="do_stuff"),
    )
    assert other_function_object.relationships == [calls_do_stuff_rel]
