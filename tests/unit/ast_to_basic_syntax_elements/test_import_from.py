from pycograph.schemas.basic_syntax_elements import (
    ABSOLUTE,
    ImportFromSyntaxElement,
    RELATIVE,
)
from pycograph.ast_to_basic_syntax_elements import parse_module


def test_import_from_absolute():
    import_code = "from sample.other import do_stuff"

    result = parse_module(import_code, "module_name")

    assert len(result) == 1
    import_from = result[0]
    assert type(import_from) == ImportFromSyntaxElement
    assert import_from.from_text == "sample.other"
    assert import_from.name == "do_stuff"
    assert import_from.level == 0
    assert import_from.name_in_importer() == "do_stuff"
    assert import_from.what_full_name() == "sample.other.do_stuff"
    assert import_from.reference_type() == ABSOLUTE


def test_import_from_with_as_absolute():
    import_code = "from sample.other import do_stuff as sth_else"

    result = parse_module(import_code, "module_name")

    assert len(result) == 1
    import_from = result[0]
    assert type(import_from) == ImportFromSyntaxElement
    assert import_from.from_text == "sample.other"
    assert import_from.name == "do_stuff"
    assert import_from.as_name == "sth_else"
    assert import_from.level == 0
    assert import_from.name_in_importer() == "sth_else"
    assert import_from.what_full_name() == "sample.other.do_stuff"
    assert import_from.reference_type() == ABSOLUTE


def test_import_from_relative():
    import_code = "from . import do_stuff"

    result = parse_module(import_code, "module_name")

    assert len(result) == 1
    import_from = result[0]
    assert type(import_from) == ImportFromSyntaxElement
    assert import_from.from_text is None
    assert import_from.name == "do_stuff"
    assert import_from.level == 1
    assert import_from.name_in_importer() == "do_stuff"
    assert import_from.what_full_name() == "do_stuff"
    assert import_from.reference_type() == RELATIVE


def test_import_from_with_as_relative():
    import_code = "from ..other import do_stuff as sth_else"

    result = parse_module(import_code, "module_name")

    assert len(result) == 1
    import_from = result[0]
    assert type(import_from) == ImportFromSyntaxElement
    assert import_from.from_text == "other"
    assert import_from.name == "do_stuff"
    assert import_from.as_name == "sth_else"
    assert import_from.level == 2
    assert import_from.name_in_importer() == "sth_else"
    assert import_from.what_full_name() == "other.do_stuff"
    assert import_from.reference_type() == RELATIVE
