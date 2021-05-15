from pycograph.project import PythonProject
from pycograph.schemas.basic_syntax_elements import ImportFromSyntaxElement
from pycograph.schemas.parse_result import ResolvedImportRelationship

from ..helper import create_module_with_content


def test_import_from_one_name():
    content = """
def do_stuff(nr):
    return nr
"""
    logic_module = create_module_with_content(content, "logic", "package")

    importer_module = create_module_with_content(
        "from package.logic import do_stuff",
        "importer",
        "package",
    )

    project = PythonProject(root_dir_path="dummy")
    project._add_module(logic_module)
    project._add_module(importer_module)

    project.parse()

    assert len(project.objects) == 3
    logic_module_object = project.objects["package.logic"]
    assert logic_module_object is not None

    importer_module_object = project.objects["package.importer"]
    imports_do_stuff_rel = ResolvedImportRelationship(
        destination_full_name="package.logic.do_stuff",
        import_element=ImportFromSyntaxElement(
            from_text="package.logic",
            name="do_stuff",
            level=0,
        ),
    )
    assert importer_module_object.relationships == [imports_do_stuff_rel]
    assert importer_module_object.names_in_scope["do_stuff"] == "package.logic.do_stuff"


def test_import_from_one_name_with_as():
    content = """
def do_stuff(nr):
    return nr
"""
    logic_module = create_module_with_content(content, "logic", "package")

    importer_module = create_module_with_content(
        "from package.logic import do_stuff as sth_else",
        "importer",
        "package",
    )

    project = PythonProject(root_dir_path="dummy")
    project._add_module(logic_module)
    project._add_module(importer_module)

    project.parse()

    assert len(project.objects) == 3
    importer_module_object = project.objects["package.importer"]
    imports_do_stuff_rel = ResolvedImportRelationship(
        destination_full_name="package.logic.do_stuff",
        import_element=ImportFromSyntaxElement(
            from_text="package.logic",
            name="do_stuff",
            as_name="sth_else",
            level=0,
        ),
    )
    assert importer_module_object.relationships == [imports_do_stuff_rel]
    assert importer_module_object.names_in_scope["sth_else"] == "package.logic.do_stuff"


def test_import_an_imported_name():
    content = """
def do_stuff(nr):
    return nr
"""
    logic_module = create_module_with_content(content, "logic", "package")

    first_importer_module = create_module_with_content(
        "from package.logic import do_stuff", "first_importer", "package"
    )
    second_importer_module = create_module_with_content(
        "from package.first_importer import do_stuff", "second_importer", "package"
    )

    project = PythonProject(root_dir_path="dummy")
    project._add_module(logic_module)
    project._add_module(first_importer_module)
    project._add_module(second_importer_module)

    project.parse()

    assert len(project.objects) == 4
    assert_imports_do_stuff(
        project, importer_module="package.first_importer", from_text="package.logic"
    )
    assert_imports_do_stuff(
        project,
        importer_module="package.second_importer",
        from_text="package.first_importer",
    )


def assert_imports_do_stuff(project, importer_module, from_text):
    importer_module_object = project.objects[importer_module]
    imports_do_stuff_rel = ResolvedImportRelationship(
        destination_full_name="package.logic.do_stuff",
        import_element=ImportFromSyntaxElement(
            from_text=from_text, name="do_stuff", level=0
        ),
    )

    assert importer_module_object.relationships == [imports_do_stuff_rel]
