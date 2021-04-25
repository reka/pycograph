from pycograph.config import settings
from pycograph.schemas.parse_result import PackageWithContext


def test_package_production_code():
    package = PackageWithContext(
        name="example",
        full_name="example",
        dir_path="",
    )

    assert package.is_test_object is False
    assert package.label() == "package"


def test_package_unit_test_no_determine_test_types():
    package = PackageWithContext(
        name="tests.unit.cli",
        full_name="tests.unit.cli",
        dir_path="",
    )

    assert package.is_test_object is True
    assert package.test_type == ""
    assert package.label() == "test_package"


def test_package_unit():
    settings.determine_test_types = True
    package = PackageWithContext(
        name="tests.unit.cli",
        full_name="tests.unit.cli",
        dir_path="",
    )

    assert package.is_test_object is True
    assert package.test_type == "unit"
    assert package.label() == "test_package"


def test_main_unit_test_package():
    settings.determine_test_types = True
    package = PackageWithContext(
        name="tests.unit",
        full_name="tests.unit",
        dir_path="",
    )

    assert package.is_test_object is True
    assert package.test_type == "unit"
    assert package.label() == "test_package"


def test_main_test_package():
    settings.determine_test_types = True
    package = PackageWithContext(
        name="tests",
        full_name="tests",
        dir_path="",
    )

    assert package.is_test_object is True
    assert package.test_type == ""
    assert package.label() == "test_package"
