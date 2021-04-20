from pycograph.schemas.basic_syntax_elements import (
    FunctionDefSyntaxElement,
    CallSyntaxElement,
)
from pycograph.ast_to_basic_syntax_elements import parse_module


def test_call_in_a_function():
    function_call_code = """
def dummy_func():
    dumbo()
"""
    result = parse_module(function_call_code, "module_name")

    assert len(result) == 1
    function_def = result[0]
    assert type(function_def) == FunctionDefSyntaxElement
    call = function_def.syntax_elements[0]
    assert type(call) == CallSyntaxElement
    assert call.what_reference_name == "dumbo"
    assert call.called_attribute is None
