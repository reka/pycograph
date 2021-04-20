from pycograph.ast_to_basic_syntax_elements import parse_module
from pycograph.schemas.basic_syntax_elements import ABSOLUTE, ImportSyntaxElement


def test_import_from():
    import_code = "import os"

    result = parse_module(import_code, "module_name")

    assert len(result) == 1
    import_element = result[0]
    assert type(import_element) == ImportSyntaxElement
    assert import_element.name == "os"
    assert import_element.name_in_importer() == "os"
    assert import_element.what_full_name() == "os"
    assert import_element.reference_type() == ABSOLUTE
