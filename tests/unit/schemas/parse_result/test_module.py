import pytest

from pycograph.exceptions import ModuleWithInvalidContentException
from pycograph.schemas.parse_result import ModuleWithContext


def test_module_with_syntax_error():
    modu = ModuleWithContext(name="example", file_path="", content="{{template")

    with pytest.raises(ModuleWithInvalidContentException):
        modu.parse()
