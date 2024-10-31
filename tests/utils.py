import os
from copy import deepcopy
from pathlib import Path

TEST_RESOURCES = (
    Path(os.path.dirname(os.path.realpath(__file__))) / "resources"
)

# Do not format, that way it can be used as copy and paste example in CLI

# fmt: off
DEFAULT_PACK_CONTEXT_STUB = {
    "challenge": {
        "slug": "challenge-slug",
        "url": "https://challenge-slug.grand-challenge.org/",
        "archives": [
            {
                "slug": "archive-slug",
                "url": "https://grand-challenge.org/archives/archive-slug/"
            },
            {
                "slug": "another-archive-slug",
                "url": "https://grand-challenge.org/archives/another-archive-slug/"
            },
            {
                "slug": "yet-another-archive-slug",
                "url": "https://grand-challenge.org/archives/yet-another-archive-slug/"
            }
        ],
        "phases": [
            {
                "slug": "phase-slug",
                "archive": {
                    "slug": "archive-slug",
                    "url": "https://grand-challenge.org/archives/archive-slug/"
                },
                "algorithm_inputs": [
                    {
                        "slug": "input-ci-slug",
                        "kind": "Segmentation",
                        "super_kind": "Image",
                        "relative_path": "images/input-value",
                        "example_value": None
                    },
                    {
                        "slug": "another-input-ci-slug",
                        "kind": "Anything",
                        "super_kind": "File",
                        "relative_path": "another-input-value.json",
                        "example_value": {"key": "value"}
                    },
                    {
                        "slug": "yet-another-input-ci-slug",
                        "kind": "Anything",
                        "super_kind": "Value",
                        "relative_path": "yet-another-input-value.json",
                        "example_value": {"key": "value"}
                    },
                    {
                        "slug": "yet-another-non-json-input-ci-slug",
                        "kind": "Anything",
                        "super_kind": "File",
                        "relative_path": "yet-another-non-json-input-value",
                        "example_value": None
                    }
                ],
                "algorithm_outputs": [
                    {
                        "slug": "output-ci-slug",
                        "kind": "Image",
                        "super_kind": "Image",
                        "relative_path": "images/output-value",
                        "example_value": None
                    },
                    {
                        "slug": "another-output-ci-slug",
                        "kind": "Anything",
                        "super_kind": "File",
                        "relative_path": "output-value.json",
                        "example_value": {"key": "value"}
                    },
                    {
                        "slug": "yet-another-output-ci-slug",
                        "kind": "Anything",
                        "super_kind": "Value",
                        "relative_path": "yet-another-output-value.json",
                        "example_value": {"key": "value"}
                    },
                    {
                        "slug": "yet-another-non-json-output-ci-slug",
                        "kind": "Anything",
                        "super_kind": "File",
                        "relative_path": "yet-another-non-json-output-value",
                        "example_value": None
                    }
                ]
            },
            {
                "slug": "another-phase-slug",
                "archive": {
                    "slug": "another-archive-slug",
                    "url": "https://grand-challenge.org/archives/another-archive-slug/"
                },
                "algorithm_inputs": [
                    {
                        "slug": "input-ci-slug",
                        "kind": "Image",
                        "super_kind": "Image",
                        "relative_path": "images/input-value",
                        "example_value": None
                    }
                ],
                "algorithm_outputs": [
                    {
                        "slug": "another-output-ci-slug",
                        "kind": "Anything",
                        "super_kind": "File",
                        "relative_path": "output-value.json",
                        "example_value": {"key": "value"}
                    }
                ]
            }
        ]
    }
}


DEFAULT_ALGORITHM_CONTEXT_STUB = {
    "algorithm": {
        "title": "An algorithm",
        "slug": "an-algorithm",
        "url": "https://grand-challenge.org/algorithms/an-algorithm/",
        "inputs": [
            {
                "slug": "input-ci-slug",
                "kind": "Segmentation",
                "super_kind": "Image",
                "relative_path": "images/input-value",
                "example_value": None
            },
            {
                "slug": "another-input-ci-slug",
                "kind": "Anything",
                "super_kind": "File",
                "relative_path": "another-input-value.json",
                "example_value": {"key": "value"}
            },
            {
                "slug": "yet-another-input-ci-slug",
                "kind": "Anything",
                "super_kind": "Value",
                "relative_path": "yet-another-input-value.json",
                "example_value": {"key": "value"}
            },
            {
                "slug": "yet-another-non-json-input-ci-slug",
                "kind": "Anything",
                "super_kind": "File",
                "relative_path": "yet-another-non-json-input-value",
                "example_value": None
            }
        ],
        "outputs": [
            {
                "slug": "output-ci-slug",
                "kind": "Image",
                "super_kind": "Image",
                "relative_path": "images/output-value",
                "example_value": None
            },
            {
                "slug": "another-output-ci-slug",
                "kind": "Anything",
                "super_kind": "File",
                "relative_path": "output-value.json",
                "example_value": {"key": "value"}
            },
            {
                "slug": "yet-another-output-ci-slug",
                "kind": "Anything",
                "super_kind": "Value",
                "relative_path": "yet-another-output-value.json",
                "example_value": {"key": "value"}
            },
            {
                "slug": "yet-another-non-json-output-ci-slug",
                "kind": "Anything",
                "super_kind": "File",
                "relative_path": "yet-another-non-json-output-value",
                "example_value": None
            }
        ]
    }
}

# fmt: on

counter = 0


def pack_context_factory(should_fail=False, **kwargs):
    global counter
    result = deepcopy(DEFAULT_PACK_CONTEXT_STUB)
    for k, v in kwargs.items():
        result["challenge"][k] = v

    def recursive_set_fail(d):
        if isinstance(d, dict):
            d["__should_fail"] = True  # Any value will do
            for item in d.values():
                recursive_set_fail(item)
        elif isinstance(d, list):
            for item in d:
                recursive_set_fail(item)

    if should_fail:
        recursive_set_fail(result)

    # Ensure unique slugs
    result["challenge"]["slug"] = result["challenge"]["slug"] + f"-{counter}"

    for phase in result["challenge"]["phases"]:
        phase["slug"] = phase["slug"] + f"-{counter}"

    counter = counter + 1
    return result


def numerical_pack_context_factory(**kwargs):
    pack_context = pack_context_factory(**kwargs)

    for archive in pack_context["challenge"]["archives"]:
        archive["slug"] = f"00-{archive['slug']}"

    for phase in pack_context["challenge"]["phases"]:
        phase["slug"] = f"00-{phase['slug']}"

        for cv in [*phase["algorithm_inputs"], *phase["algorithm_outputs"]]:
            cv["slug"] = f"00-{cv['slug']}"

    return pack_context


def algorithm_template_context_factory(should_fail=False, **kwargs):
    global counter
    result = deepcopy(DEFAULT_ALGORITHM_CONTEXT_STUB)
    for k, v in kwargs.items():
        result["algorithm"][k] = v

    def recursive_set_fail(d):
        if isinstance(d, dict):
            d["__should_fail"] = True  # Any value will do
            for item in d.values():
                recursive_set_fail(item)
        elif isinstance(d, list):
            for item in d:
                recursive_set_fail(item)

    if should_fail:
        recursive_set_fail(result)

    return result
