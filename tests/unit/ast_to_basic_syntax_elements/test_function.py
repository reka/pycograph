from pycograph.schemas.basic_syntax_elements import (
    ClassDefSyntaxElement,
    FunctionDefSyntaxElement,
)
from pycograph.ast_to_basic_syntax_elements import parse_module


def test_function_in_module():
    function_def_code = """
def answer():
    return 42
"""

    result = parse_module(function_def_code, "module_name")

    assert len(result) == 1
    function_def = result[0]
    assert type(function_def) == FunctionDefSyntaxElement
    assert function_def.name == "answer"


def test_function_in_class():
    class_with_function_def_code = """
class Example:
    def answer():
        return 42
"""

    result = parse_module(class_with_function_def_code, "module_name")

    assert len(result) == 1
    class_def = result[0]
    assert type(class_def) == ClassDefSyntaxElement
    assert class_def.name == "Example"
    function_def = class_def.syntax_elements[0]
    assert type(function_def) == FunctionDefSyntaxElement
    assert function_def.name == "answer"
