# Contributing

Thanks a lot for contributing to Pycograph.

## Environment Setup: Redis

You'll need:

* a running instance of Redis with the RedisGraph module
* a running instance of RedisInsight

The easiest way to start them is via Docker Compose (from the root of this project):

```
docker-compose up
```

## Poetry

The recommended way of working on this project is with [Poetry](https://python-poetry.org/).  
To install Poetry, see the [documentation](https://python-poetry.org/docs/#installation)

Now, you can set up your environment:

```
poetry shell
poetry install
```

Now, you can:

* execute the `pycograph` command
* run the tests with `pytest`
* format the code with `black .`

## Alternative Virtual Environments

If you prefer to use another tool for virtual environments, you can install the dependencies via:

```
pip install -r devtools/requirements.txt
```

You also need to install the project itself with:

```
pip install .
```

`devtools/requirements.txt` is generated via `poetry export`. It contains all the dev dependencies as well. Its purpose is to make development without Poetry easier. The "source of truth" regarding requirements is `pyproject.toml`

## Tests

There are 3 levels of tests:

* unit
* integration
* integration tests based on a sample project in the `test_data` directory

The current code coverage target is 90%.  
Each new feature should contain some unit or integration tests.

## Code Conventions

* formatter: Black
* type hints via mypy

A suggested pre-commit hook is available at `devtools/git-hooks/pre-commit`