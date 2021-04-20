from pycograph.project import PythonProject
from pycograph.schemas.basic_syntax_elements import CallSyntaxElement
from pycograph.schemas.parse_result import CallsRelationship, PackageWithContext
from ..helper import create_module_with_content


def test_import_and_call():
    content = """
def do_stuff(nr):
    return nr
"""
    logic_module = create_module_with_content(content, "logic", "package")

    importer_content = """
import package

def other():
    package.logic.do_stuff()
"""
    importer_module = create_module_with_content(
        importer_content,
        "importer",
        "package",
    )
    pkg = PackageWithContext(
        name="package",
        full_name="package",
        dir_path="",
    )

    project = PythonProject(root_dir_path="dummy")
    project.modules = [logic_module, importer_module]
    project._add_object(pkg)
    project._add_object(logic_module)
    project._add_object(importer_module)

    project.parse()

    assert len(project.objects) == 5

    other_function_object = project.objects["package.importer.other"]
    calls_logic_rel = CallsRelationship(
        destination_full_name="package.logic",
        syntax_element=CallSyntaxElement(
            what_reference_name="package", called_attribute="logic"
        ),
    )
    calls_package_rel = CallsRelationship(
        destination_full_name="package",
        syntax_element=CallSyntaxElement(what_reference_name="package"),
    )
    # Expected behavior: It should also find a call to package.logic.do_stuff
    assert other_function_object.relationships == [calls_logic_rel, calls_package_rel]
