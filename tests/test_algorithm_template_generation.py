import glob
import subprocess
import uuid
from contextlib import nullcontext

import pytest

from grand_challenge_forge.forge import generate_algorithm_template
from tests.utils import (
    _test_save,
    _test_script,
    add_fail_flags,
    add_numerical_slugs,
    algorithm_template_context_factory,
)


def test_for_algorithm_template_content(tmp_path):
    context = algorithm_template_context_factory()
    template_path = generate_algorithm_template(
        context=context,
        output_path=tmp_path,
    )

    for filename in [
        "Dockerfile",
        "README.md",
        "resources",
        "inference.py",
        "requirements.txt",
        "do_build.sh",
        "do_save.sh",
        "do_test_run.sh",
    ]:
        assert (template_path / filename).exists()


def test_algorithm_template_run_permissions(tmp_path):
    context = algorithm_template_context_factory()
    template_path = generate_algorithm_template(
        context=context,
        output_path=tmp_path,
    )

    # Run it twice to ensure all permissions are correctly handled
    for _ in range(0, 2):
        _test_script(
            script_path=template_path / "do_test_run.sh",
            extra_arg=f"test-{uuid.uuid4()}",  # Ensure unique build and tests
        )

        # Check if output is generated (ignore content)
        output_dir = template_path / "test" / "output"
        for output in context["algorithm"]["outputs"]:
            expected_file = output_dir / output["relative_path"]
            assert expected_file.exists()


@pytest.mark.parametrize(
    "context, context_manager",
    [
        (
            algorithm_template_context_factory(),
            nullcontext(),
        ),
        (
            add_numerical_slugs(algorithm_template_context_factory()),
            nullcontext(),
        ),
        (
            add_fail_flags(algorithm_template_context_factory()),
            pytest.raises(subprocess.CalledProcessError),
        ),
    ],
)
def test_algorithm_template_run(context, context_manager, tmp_path):
    template_path = generate_algorithm_template(
        context=context,
        output_path=tmp_path,
    )

    with context_manager:
        _test_script(
            script_path=template_path / "do_test_run.sh",
            extra_arg=f"test-{uuid.uuid4()}",  # Ensure unique build and tests
        )

        output_dir = template_path / "test" / "output"
        # Check if output is generated (ignore content)
        for output in context["algorithm"]["outputs"]:
            expected_file = output_dir / output["relative_path"]
            assert expected_file.exists()


@pytest.mark.parametrize(
    "context, context_manager",
    [
        (
            algorithm_template_context_factory(),
            nullcontext(),
        ),
        (
            add_numerical_slugs(algorithm_template_context_factory()),
            nullcontext(),
        ),
        (
            add_fail_flags(algorithm_template_context_factory()),
            pytest.raises(subprocess.CalledProcessError),
        ),
    ],
)
def test_algorithm_template_save(context, context_manager, tmp_path):
    template_path = generate_algorithm_template(
        context=context,
        output_path=tmp_path,
    )

    with context_manager:
        custom_image_tag = _test_save(script_dir=template_path)

        # Check if saved image exists
        pattern = str(template_path / f"{custom_image_tag}_*.tar.gz")
        matching_files = glob.glob(pattern)
        assert len(matching_files) == 1, (
            f"Algorithm template do_save.sh does not generate the exported "
            f"image matching: {pattern}"
        )
