# Pycograph

[![PyPI version](https://badge.fury.io/py/pycograph.svg)](https://badge.fury.io/py/pycograph)
![Black](https://img.shields.io/badge/code%20style-black-000000.svg)

![Pycograph](https://github.com/reka/pycograph/raw/main/resources/pycograph_logo.png)

Homepage: [https://pycograph.com/](https://pycograph.com/)  
PyPI: [https://pypi.org/project/pycograph/](https://pypi.org/project/pycograph/)

**Explore your Python code with graph queries**

Pycograph creates a [RedisGraph](https://oss.redislabs.com/redisgraph/) model of your Python code. You can: 

* query it with [Cypher](https://oss.redislabs.com/redisgraph/commands/)
* visualize it with [RedisInsight](https://redislabs.com/redis-enterprise/redis-insight/)

![sample Redis Insight result](https://github.com/reka/pycograph/raw/main/resources/sample_redis_insight.png)

## Getting Started

Requirements:

* Python 3.8 or higher
* a Redis instance with the RedisGraph module (local, remote or via Docker)
* not strictly necessary, but recommended: RedisInsight for visualizing the query results

Install Pycograph from PyPI:

```
pip install pycograph
```

Start a Redis instance with the RedisGraph module and RedisInsight. E.g. via Docker containers:

```
docker run -d -p 6379:6379 redislabs/redismod
docker run -d -v redisinsight:/db -p 8001:8001 redislabs/redisinsight:latest
```

Visit your RedisInstance at http://localhost:8001 in a browser.  
Connect to your local Redis database.

Create a RedisGraph model of your project's code with the `pycograph load` command:

```
pycograph load --project-dir ~/code/your-project --test-types
```

By default, if you don't provide the `--project-dir` option, Pycograph tries to find Python code in the current working directory.  


Run a query in RedisInsight. E.g.

```
GRAPH.QUERY "your-project" "MATCH (n) return n"
```

To see some more advanced queries, check out the [examples](https://pycograph.com/examples/) at pycograph.com

## Options

* `--project-dir`: The root directory of the Python project you want to analyze. If you omit this option, Pycograph will search for `.py` files in your current working directory.
* `--graph-name`: Specifies the name of the generated graph. Default: the name of the project directory.
* `--overwrite`: If a graph with this name exists overwrite it. If you don't provide this flag, the new nodes and edges will be appended to the graph.
* `--test-types`: Determine the types of tests based on the subdirectories of the `tests` directory.
* `--redis-host`: The host of the Redis instance. Default: localhost
* `--redis-port`: The port of the Redis instance. Default: 6379 
* `--version`: Print Pycograph version and exit.

## Limitations

Pycograph is in beta version.

It creates a basic model with focus on the relationships betweeen the different parts of the code base. Even that model might be incomplete, ignoring some less common syntax. The goal is to provide some useful insight, not to create an exhaustive model.

If Pycograph finds a syntax error, it skips the module containing the syntax error and tries to build a model from the rest of the code base.

Below are some of the limitations. If you bump into other limitations, please open a GitHub issue.

### Imports

The following imports will be ignored by Pycograph:

* imported external packages
* `import *` syntax
* variables
* globals

### Calls

* All the limitations of the imports.
* Resolving longer calls of more than 2 levels.

### Other Known Limitations

* No support for `.py` files containing Jinja templates (e.g. cookiecutter)
* Inner functions are ignored.

## How Does It Work?

![Pycograph architecture](https://raw.githubusercontent.com/reka/pycograph/main/resources/pycograph_architecture.png)

### Libraries used:

* [ast](https://docs.python.org/3/library/ast.html) module of the Python standard library for the abstract syntax tree
* [Pydantic](https://pydantic-docs.helpmanual.io) both for the models of the intermediate objects and for the settings
* [redisgraph-py](https://github.com/RedisGraph/redisgraph-py) for creating the RedisGraph model
* [typer](https://typer.tiangolo.com/) for the command line interface

## Contributing

see the [Contributing guide](https://github.com/reka/pycograph/blob/main/CONTRIBUTING.md)