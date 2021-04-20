from pycograph.schemas.basic_syntax_elements import ClassDefSyntaxElement
from pycograph.ast_to_basic_syntax_elements import parse_module


def test_define_a_class():
    class_def_code = """
class Example:
    pass
"""

    result = parse_module(class_def_code, "module_name")

    assert len(result) == 1
    class_def = result[0]
    assert type(class_def) == ClassDefSyntaxElement
    assert class_def.name == "Example"
