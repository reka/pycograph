import pytest

from tests.integration.helper import create_module_with_content


@pytest.fixture
def module_with_content(content):
    return create_module_with_content(content)
