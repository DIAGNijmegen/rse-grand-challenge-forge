[![CI](https://github.com/DIAGNijmegen/rse-grand-challenge-forge/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/DIAGNijmegen/rse-grand-challenge-forge/actions/workflows/ci.yml/badge.svg?branch=main)
[![PyPI](https://img.shields.io/pypi/v/grand-challenge-forge)](https://pypi.org/project/grand-challenge-forge/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/grand-challenge-forge)](https://pypi.org/project/grand-challenge-forge/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

#  🛠️ grand-challenge-forge

A utility that generates distributable items that help challenge organizers set up their challenge more easily on
[Grand-Challenge.org](https://grand-challenge.org/).

## Install

Install via PyPi:

```shell
pip install grand-challenge-forge
grand-challenge-forge --help
```

## 🎒 Challenge packs

A challenge pack consists of challenge-tailored examples for the following:
* A script to _automate uploading_ data to an archive
* A _submission algorithm_ that can be submitted to a challenge phase
* An _evaluation method_ that evaluates algorithm submissions and generates performance
  metrics for ranking


### Usage
```shell
grand-challenge-forge pack-context.json
```
Will use the context found in `pack-context.json` and generate a pack at the current working directory in
a directory `dist/` (default).

<details>

<summary> Example of the content of pack-context.json </summary>

```JSON
{
    "challenge": {
        "slug": "challenge-slug",
        "phases": [
            {
                "slug": "phase-slug",
                "archive": {
                    "url": "https://grand-challenge.org/archives/archive-slug/"
                },
                "inputs": [
                    {
                        "slug": "input-ci-slug",
                        "kind": "Segmentation",
                        "super_kind": "Image",
                        "relative_path": "images/input-value"
                    },
                    {
                        "slug": "another-input-ci-slug",
                        "kind": "Anything",
                        "super_kind": "File",
                        "relative_path": "another-input-value.json"
                    }
                ],
                "outputs": [
                    {
                        "slug": "output-ci-slug",
                        "kind": "Image",
                        "super_kind": "Image",
                        "relative_path": "images/output-value"
                    },
                    {
                        "slug": "another-output-ci-slug",
                        "kind": "Anything",
                        "super_kind": "File",
                        "relative_path": "output-value.json"
                    }
                ]
            },
            {
                "slug": "another-phase-slug",
                "archive": {
                    "url": "https://grand-challenge.org/archives/another-archive-slug/"
                },
                "inputs": [
                    {
                        "slug": "input-ci-slug",
                        "kind": "Image",
                        "super_kind": "Image",
                        "relative_path": "images/input-value"
                    }
                ],
                "outputs": [
                    {
                        "slug": "another-output-ci-slug",
                        "kind": "Anything",
                        "super_kind": "File",
                        "relative_path": "output-value.json"
                    }
                ]
            }
        ]
    }
}
```
</details>

Alternatively, you generate a pack by providing a JSON string directly:

```shell
grand-challenge-forge --output-dir /tmp '{ "challenge": { "slug": "a-slug"...'
```
This will output a pack directory in the `/tmp` directory.

> [!NOTE]
> By default, the forge does quality checks on the pack that may require docker.
> You can disable these via `-n`

## 🏗️ Development

### Install locally
Install locally grand-challenge-forge locally (requires `poetry`):

```shell
git clone https://github.com/DIAGNijmegen/rse-grand-challenge-forge.git
cd rse-grand-challenge-forge
poetry install
poetry run grand-challenge-forge --help
```

### Pre-commit hooks
Several linters and stylers run to check the formating during continuous integration. Ensure they are run before
committing by installing [pre-commit](https://pre-commit.com/).


### Running Tests
use `tox` to run all tests across all supported python versions:
```
$ pip install tox
$ tox
```

### Dependencies
Under the hood grand-challenge-forge uses:
* [Click](https://palletsprojects.com/p/click/)
  * a composable command line interface toolkit
* [Cookiecutter](https://github.com/cookiecutter/cookiecutter)
  * a utility that creates projects from project templates
