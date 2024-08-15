
# ShopiPy
Retrieve and parse Shopify order data, retrieve the assets needed for the order, and create a PDF to send to the printer. It gives the user the ability to add custom orders from other vendors to this list and will outline any filed that are missing.

[![CI](https://github.com/sjriddle/shopipy/actions/workflows/main.yml/badge.svg)](https://github.com/sjriddle/shopipy/actions/workflows/main.yml)

## Installation & Setup
Here's the step-by-step guide to install and set up the application.

### Makefile Commands
To simplify the installation and setup process, we use a `Makefile` that contains all the necessary commands to install dependencies, run tests, and perform other common operations. Here's an overview of the available commands:
```bash
  help:             ## Show the help.
  show:             ## Show the current environment.
  install:          ## Install the project in dev mode.
  fmt:              ## Format code using black & isort.
  lint:             ## Run pep8, black, mypy linters.
  test: lint        ## Run tests and generate coverage report.
  watch:            ## Run tests on every change.
  clean:            ## Clean unused files.
  virtualenv:       ## Create a virtual environment.
  release:          ## Create a new tag for release.
  docs:             ## Build the documentation.
  switch-to-poetry: ## Switch to poetry package manager.
  init:             ## Initialize the project based on an application template.
```


To install the application and its dependencies, you can run:
```bash
make install
```

This command will install all the dependencies required for the application, including `shopipy`.

# Usage

To use the application, you can refer to the `Makefile` for the most common operations. Here's how you can run the application:

```bash
make run
```

This command will start the application, making it ready for use.

## Running Tests

Testing is an essential part of development. To run the tests for this application, you can use:

```bash
make test
```

This will execute all the tests defined in the project, ensuring that your application is working as expected.

## Development

For developers looking to contribute to the project, the `Makefile` also includes commands to set up a development environment and perform common development tasks:

- **Setup Development Environment**: To set up your development environment, run:

  ```bash
  make dev-setup
  ```

- **Linting**: To check the code for any linting errors, use:

  ```bash
  make lint
  ```

- **Cleaning**: To clean up the project (e.g., removing temporary files), you can run:

  ```bash
  make clean
  ```

Refer to the `Makefile` for a full list of available commands and their descriptions. This approach ensures that all the necessary operations for installation, testing, and development are streamlined and easily accessible.
## Install it from PyPI

```bash
pip install shopipy
```

## Usage

```py
from shopipy import BaseClass
from shopipy import base_function

BaseClass().base_method()
base_function()
```

```bash
$ python -m shopipy
#or
$ shopipy
```

## Development

Read the [CONTRIBUTING.md](CONTRIBUTING.md) file.
