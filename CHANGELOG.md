# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - 2021-08-10
### Added

* basic support for function call directly in a module
* test for the current limitation: no syntax element for assigning value to an attribute
* whole_project tests: introduce assert_node test helper function
* various further test cases

### Changed

* redis_graph.commit(): improve error handling
* increased coverage target: 94%
* syntax changes suggested by Sourcery

## [0.2.12] - 2021-05-01
### Added

* basic support for function call directly in a module
* error handling: invalid project dir, no .py file in the project dir
* add isort incl. GitHub action
* Black version update and GitHub action
* coverage: add target 90%

## [0.2.11] - 2021-04-25
### Added

* add flake8 incl. GitHub action
* fix errors found by flake8

## [0.2.10] - 2021-04-24
### Added

* support for resolving multiple level function calls e.g. `package.logic.do_stuff()`
* CHANGELOG

## [0.2.9] - 2021-04-23
### Added

* Codecov configuration

## [0.2.8] - 2021-04-22
### Changed

* some documentation

## [0.2.7] - 2021-04-22
### Added

* basic GitHub Actions workflow

## [0.2.6] - 2021-04-22
### Added

* error handling for Redis instance not supporting `GRAPH` commands
* error handling for ResponseError from the RedisGraph client library
* docstrings

## [0.2.5] - 2021-04-21
### Added

* devtools/requirements.txt
* pre-commit hook to generate devtools/requirements.txt
* info about contributing using a development environment without Poetry

## [0.2.3] - 2021-04-21
### Added

* README: PyPI and Black badges
* README: links to homepage

### Changed

* README: relative links => absolute links

## [0.2.2] - 2021-04-20
### Added

* project metadata

## [0.2.1] - 2021-04-20
### Added

* PyPI config


## [0.2.0] - 2021-04-20
### Added

* a basic RedisGraph model representing a Python project
* nodes: packages, modules, functions, classes, constants
* edges: contains, imports, calls
* distinction between test and production code
* distinction between different test types