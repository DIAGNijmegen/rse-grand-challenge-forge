import glob
import os
import subprocess
import uuid
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from grand_challenge_forge import RESOURCES_PATH

DEBUG = os.getenv("DEBUG", "false").lower() == "true"

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
                "example_value": "A string that needs to be escaped"
            }
        ]
    }
}

# fmt: on

counter = 0


def make_slugs_unique(d):
    """Add counter to all slugs in the structure to make them unique."""
    global counter
    if isinstance(d, dict):
        if "slug" in d:
            d["slug"] = f"{d['slug']}-{counter}"
        for item in d.values():
            make_slugs_unique(item)
    elif isinstance(d, list):
        for item in d:
            make_slugs_unique(item)
    return d


def add_fail_flags(d):
    """Add fail flags to all dictionaries and lists in the structure."""
    if isinstance(d, dict):
        d["__should_fail"] = True  # Any value will do
        for item in d.values():
            add_fail_flags(item)
    elif isinstance(d, list):
        for item in d:
            add_fail_flags(item)
    return d


def add_numerical_slugs(d):
    """Add '00-' prefix to all slugs in the structure."""
    if isinstance(d, dict):
        if "slug" in d:
            d["slug"] = f"00-{d['slug']}"
        for item in d.values():
            add_numerical_slugs(item)
    elif isinstance(d, list):
        for item in d:
            add_numerical_slugs(item)
    return d


def pack_context_factory(**kwargs):
    result = deepcopy(DEFAULT_PACK_CONTEXT_STUB)
    result["challenge"].update(kwargs)

    # Generate phases using phase_context_factory
    result["challenge"]["phases"] = [
        phase_context_factory(archive=phase["archive"])["phase"]
        for phase in result["challenge"]["phases"]
    ]

    return make_slugs_unique(result)


def phase_context_factory(**kwargs):
    # Create a phase context from the first phase in the default pack context
    result = deepcopy(DEFAULT_PACK_CONTEXT_STUB["challenge"]["phases"][0])
    result.update(kwargs)
    return make_slugs_unique({"phase": result})


def algorithm_template_context_factory(**kwargs):
    result = deepcopy(DEFAULT_ALGORITHM_CONTEXT_STUB)
    result["algorithm"].update(kwargs)
    return make_slugs_unique(result)


def _test_script(
    *,
    script_path,
    extra_arg=None,
):
    """Test a subprocess execution.

    Args
    ----
        script_path: The path to the script to execute
        extra_arg: Optional additional argument to pass to the script

    """
    command = [script_path]
    if extra_arg:
        command.append(extra_arg)

    result = subprocess.run(
        command,
        capture_output=True,
        check=True,  # This will raise CalledProcessError if returncode != 0
    )
    if result.stderr:
        raise subprocess.CalledProcessError(
            returncode=0,
            cmd=command,
            stderr=result.stderr,
            output=result.stdout,
        )


def _test_save(script_dir):
    """Test the save functionality of a script directory.

    Args
    ----
        script_dir: The directory containing the script to test

    """
    # Running multiple tests at the same time.
    custom_image_tag = f"test-{uuid.uuid4()}"

    pattern = str(script_dir / f"{custom_image_tag}_*.tar.gz")
    matching_files = glob.glob(pattern)

    assert len(matching_files) == 0

    mocks_bin = RESOURCES_PATH / "mocks" / "bin"
    current_path = os.environ.get("PATH", "")
    extended_path = f"{mocks_bin}:{current_path}"

    with patch.dict("os.environ", PATH=extended_path):
        _test_script(
            script_path=script_dir / "do_save.sh",
            extra_arg=custom_image_tag,
        )

    return custom_image_tag
