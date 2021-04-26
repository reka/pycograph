from pycograph.exceptions import RedisWithoutGraphException
import pytest
from typer.testing import CliRunner

from pycograph import __version__
from pycograph.cli import app
from pycograph.config import settings

runner = CliRunner()


def test_load_without_options(load_mock):
    result = runner.invoke(app, ["load"])

    load_mock.assert_called_once_with(None, None)
    assert result.exit_code == 0
    assert "Graph successfully updated." in result.stdout


def test_load_project_dir(load_mock):
    project_dir = "~/projects/sample"
    result = runner.invoke(app, ["load", "--project-dir", project_dir])

    load_mock.assert_called_once_with(project_dir, None)
    assert result.exit_code == 0
    assert "Graph successfully updated." in result.stdout


def test_load_graph_name(load_mock):
    result = runner.invoke(app, ["load", "--graph-name", "sample-graph"])

    load_mock.assert_called_once_with(None, "sample-graph")
    assert result.exit_code == 0
    assert "Graph successfully updated." in result.stdout


def test_load_host_and_port(load_mock):
    result = runner.invoke(
        app, ["load", "--redis-host", "dummyhost", "--redis-port", 10001]
    )

    assert settings.redis_host == "dummyhost"
    assert settings.redis_port == 10001
    load_mock.assert_called_once_with(None, None)
    assert result.exit_code == 0
    assert "Graph successfully updated." in result.stdout


def test_load_raises_error(load_mock, mocker):
    load_mock.side_effect = RedisWithoutGraphException()
    echo_mock = mocker.patch("typer.echo")
    result = runner.invoke(app, ["load"])

    load_mock.assert_called_once_with(None, None)
    echo_mock.assert_called_once_with(load_mock.side_effect, err=True)
    assert len(result.stdout) == 0


def test_load_version(load_mock):
    result = runner.invoke(app, ["load", "--version"])

    load_mock.assert_not_called()
    assert result.exit_code == 0
    assert __version__ in result.stdout


def test_version(load_mock):
    result = runner.invoke(app, ["--version"])

    load_mock.assert_not_called()
    assert result.exit_code == 0
    assert __version__ in result.stdout


@pytest.fixture
def load_mock(mocker):
    return mocker.patch("pycograph.pycograph.load")
