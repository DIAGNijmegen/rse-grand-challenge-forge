import glob
from pathlib import Path

import pytest

from grand_challenge_forge.forge import generate_algorithm_template
from tests.utils import (
    _test_script_run,
    add_numerical_slugs,
    algorithm_template_context_factory,
    mocked_binaries,
    zipfile_to_filesystem,
)


def test_for_algorithm_template_content(tmp_path):
    with zipfile_to_filesystem(output_path=tmp_path) as zip_file:
        template_zdir = generate_algorithm_template(
            context=algorithm_template_context_factory(),
            output_zip_file=zip_file,
            output_zpath=Path(""),
        )

    template_path = tmp_path / template_zdir

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
    algorithm_template_context = algorithm_template_context_factory()
    with zipfile_to_filesystem(output_path=tmp_path) as zip_file:
        template_zdir = generate_algorithm_template(
            context=algorithm_template_context,
            output_zip_file=zip_file,
            output_zpath=Path(""),
        )

    template_path = tmp_path / template_zdir

    # Run it twice to ensure all permissions are correctly handled
    for _ in range(0, 2):
        _test_script_run(
            script_path=template_path / "do_test_run.sh",
        )

        # Check if output is generated (ignore content)
        output_dir = template_path / "test" / "output"
        for output in algorithm_template_context["algorithm"]["outputs"]:
            expected_file = output_dir / output["relative_path"]
            assert expected_file.exists()


@pytest.mark.parametrize(
    "context",
    [
        algorithm_template_context_factory(),
        add_numerical_slugs(algorithm_template_context_factory()),
    ],
)
def test_algorithm_template_run(context, tmp_path):
    with zipfile_to_filesystem(output_path=tmp_path) as zip_file:
        template_zdir = generate_algorithm_template(
            context=context,
            output_zip_file=zip_file,
            output_zpath=Path(""),
        )

    template_path = tmp_path / template_zdir

    _test_script_run(script_path=template_path / "do_test_run.sh")

    output_dir = template_path / "test" / "output"
    # Check if output is generated (ignore content)
    for output in context["algorithm"]["outputs"]:
        expected_file = output_dir / output["relative_path"]
        assert expected_file.exists()


@pytest.mark.parametrize(
    "context",
    [
        algorithm_template_context_factory(),
        add_numerical_slugs(algorithm_template_context_factory()),
    ],
)
def test_algorithm_template_save(context, tmp_path):
    with zipfile_to_filesystem(output_path=tmp_path) as zip_file:
        template_zdir = generate_algorithm_template(
            context=context,
            output_zip_file=zip_file,
            output_zpath=Path(""),
        )

    template_path = tmp_path / template_zdir

    with mocked_binaries():
        _test_script_run(script_path=template_path / "do_save.sh")

    # Check if saved image exists
    pattern = str(template_path / f"{context['algorithm']['slug']}_*.tar.gz")
    matching_files = glob.glob(pattern)
    assert len(matching_files) == 1, (
        f"Algorithm template do_save.sh does not generate the exported "
        f"image matching: {pattern}"
    )
