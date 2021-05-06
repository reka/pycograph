from pycograph.project import PythonProject
from pycograph.schemas.basic_syntax_elements import ABSOLUTE, ImportSyntaxElement
from pycograph.schemas.parse_result import (
    PackageWithContext,
    ResolvedImportRelationship,
)

from ..helper import create_module_with_content


def test_import_one_name():
    content = """
def do_stuff(nr):
    return nr
"""
    logic_module = create_module_with_content(content, "logic", "package")

    importer_module = create_module_with_content(
        "import package",
        "importer",
        "package",
    )
    pkg = PackageWithContext(
        name="package",
        full_name="package",
        dir_path="",
    )

    project = PythonProject(root_dir_path="dummy")
    project._add_object(pkg)
    project._add_module(logic_module)
    project._add_module(importer_module)

    project.parse()

    assert len(project.objects) == 4
    logic_module_object = project.objects["package.logic"]
    assert logic_module_object is not None

    importer_module_object = project.objects["package.importer"]
    imports_do_stuff_rel = ResolvedImportRelationship(
        destination_full_name="package",
        import_element=ImportSyntaxElement(
            name="package",
        ),
    )
    assert imports_do_stuff_rel.properties() == {
        "name": "package",
        "as_name": "",
        "reference_type": ABSOLUTE,
    }
    assert importer_module_object.relationships == [imports_do_stuff_rel]
    assert importer_module_object.names_in_scope["package"] == "package"
