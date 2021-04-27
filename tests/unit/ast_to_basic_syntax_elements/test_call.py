from pycograph.schemas.basic_syntax_elements import (
    FunctionDefSyntaxElement,
    CallSyntaxElement,
)
from pycograph.ast_to_basic_syntax_elements import parse_module


def test_call_directly_in_a_module():
    function_call_code = "dumbo()"

    result = parse_module(function_call_code, "module_name")

    dumbo_call = CallSyntaxElement(what_reference_name="dumbo")
    assert result == [dumbo_call]


def test_call_in_a_function():
    function_call_code = """
def dummy_func():
    dumbo()
"""
    result = parse_module(function_call_code, "module_name")

    assert len(result) == 1
    function_def = result[0]
    assert type(function_def) == FunctionDefSyntaxElement
    dumbo_call = CallSyntaxElement(what_reference_name="dumbo")
    assert function_def.syntax_elements == [dumbo_call]


def test_nested_call_in_a_function():
    function_call_code = """
def dummy_func():
    dumbo(other())
"""
    result = parse_module(function_call_code, "module_name")

    assert len(result) == 1
    function_def = result[0]
    assert type(function_def) == FunctionDefSyntaxElement
    dumbo_call = CallSyntaxElement(what_reference_name="dumbo")
    other_call = CallSyntaxElement(what_reference_name="other")
    assert function_def.syntax_elements == [dumbo_call, other_call]


def test_call_with_attribute():
    function_call_code = """
def dummy_func():
    obj.dummy()
"""

    result = parse_module(function_call_code, "module_name")

    assert len(result) == 1
    function_def = result[0]
    assert type(function_def) == FunctionDefSyntaxElement
    call_dummy = CallSyntaxElement(what_reference_name="obj", called_attribute="dummy")
    call_obj = CallSyntaxElement(what_reference_name="obj")
    assert function_def.syntax_elements == [call_dummy, call_obj]
