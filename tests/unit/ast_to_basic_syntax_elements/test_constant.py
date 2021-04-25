from pycograph.ast_to_basic_syntax_elements import parse_module
from pycograph.schemas.basic_syntax_elements import ConstantSyntaxElement


def test_define_a_constant():
    single_constant_assignment = """
ANSWER =  42
"""
    result = parse_module(single_constant_assignment, "module_name")

    assert len(result) == 1
    only_defined_thing = result[0]
    assert type(only_defined_thing) == ConstantSyntaxElement
    assert only_defined_thing.name == "ANSWER"
