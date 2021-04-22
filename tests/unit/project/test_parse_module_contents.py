from pycograph.project import PythonProject
from pycograph.schemas.parse_result import ConstantWithContext, ModuleWithContext


def test_valid_and_invalid_module(mocker):
    error_logger = mocker.patch("pycograph.project.logger.error")
    valid_modu = ModuleWithContext(
        name="example", full_name="example", file_path="", content="ANSWER=42"
    )
    invalid_modu = ModuleWithContext(
        name="other", full_name="other", file_path="", content="{{template"
    )
    project = PythonProject("")
    project._add_module(valid_modu)
    project._add_module(invalid_modu)

    project._parse_module_contents()

    # Valid module: Its content has been parsed and added:
    assert len(project.objects) == 3
    assert type(project.objects.get("example.ANSWER")) == ConstantWithContext
    # Invalid module: An error has been logged:
    error_logger.assert_called_once_with(
        "Skipped module other because of syntax error."
    )
