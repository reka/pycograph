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
    project.modules = [logic_module, importer_module]
    project._add_object(logic_module)
    project._add_object(importer_module)

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
    project.modules = [logic_module, importer_module]
    project._add_object(logic_module)
    project._add_object(importer_module)

    project.parse()

    assert len(project.objects) == 4

    other_function_object = project.objects["package.importer.other"]
    calls_do_stuff_rel = CallsRelationship(
        destination_full_name="package.logic.do_stuff",
        syntax_element=CallSyntaxElement(what_reference_name="sth_else"),
    )
    assert other_function_object.relationships == [calls_do_stuff_rel]
