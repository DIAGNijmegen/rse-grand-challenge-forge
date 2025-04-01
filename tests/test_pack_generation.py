import glob
import subprocess
import uuid
from contextlib import nullcontext
from unittest.mock import MagicMock, patch

import pytest

from grand_challenge_forge.forge import (
    generate_challenge_pack,
    generate_example_algorithm,
    generate_example_evaluation,
    generate_upload_to_archive_script,
)
from grand_challenge_forge.utils import (
    change_directory,
    directly_import_module,
)
from tests.utils import (
    _test_save,
    _test_script,
    add_fail_flags,
    add_numerical_slugs,
    pack_context_factory,
    phase_context_factory,
)


def test_for_pack_content(tmp_path):
    context = pack_context_factory()
    pack_path = generate_challenge_pack(
        context=context,
        output_path=tmp_path,
    )

    assert (pack_path / "README.md").exists()

    for phase in context["challenge"]["phases"]:
        assert (pack_path / phase["slug"]).exists()

        assert (
            pack_path
            / phase["slug"]
            / f"upload-to-archive-{phase['archive']['slug']}"
        ).exists()

        assert (pack_path / phase["slug"] / "example-algorithm").exists()

        eval_path = pack_path / phase["slug"] / "example-evaluation-method"
        assert eval_path.exists()
        assert (eval_path / "test" / "input" / "predictions.json").exists()


@pytest.mark.parametrize(
    "phase_context, context",
    [
        (
            phase_context_factory(),
            nullcontext(),
        ),
        (
            add_numerical_slugs(phase_context_factory()),
            nullcontext(),
        ),
        (
            add_fail_flags(phase_context_factory()),
            pytest.raises(ZeroDivisionError),
        ),
    ],
)
def test_pack_upload_to_archive_script(phase_context, context, tmp_path):
    """Checks if the upload to archive script works as intended"""

    script_dir = generate_upload_to_archive_script(
        context=phase_context,
        output_path=tmp_path,
    )
    with context:
        with change_directory(script_dir):
            gcapi = MagicMock()
            with patch.dict("sys.modules", gcapi=gcapi):
                # Load the script as a module
                upload_files = directly_import_module(
                    name="upload_files",
                    path=script_dir / "upload_files.py",
                )

                # Run the script, but noop print
                def debug_print(arg):
                    pass

                with patch("builtins.print", debug_print):
                    upload_files.main()

            # Assert that it reaches out via gcapi
            gcapi.Client.assert_called()
            gcapi.Client().archive_items.create.assert_called()
            gcapi.Client().update_archive_item.assert_called()


def test_pack_example_algorithm_run_permissions(tmp_path):
    phase_context = phase_context_factory()

    algorithm_dir = generate_example_algorithm(
        context=phase_context,
        output_path=tmp_path,
    )

    # Run it twice to ensure all permissions are correctly handled
    for _ in range(0, 2):
        _test_script(
            script_path=algorithm_dir / "do_test_run.sh",
            extra_arg=f"test-{uuid.uuid4()}",  # Ensure unique build and tests
        )

        # Check if output is generated (ignore content)
        output_dir = algorithm_dir / "test" / "output"
        for output in phase_context["phase"]["algorithm_outputs"]:
            expected_file = output_dir / output["relative_path"]
            assert expected_file.exists()


@pytest.mark.parametrize(
    "phase_context, context",
    [
        (
            phase_context_factory(),
            nullcontext(),
        ),
        (
            add_numerical_slugs(phase_context_factory()),
            nullcontext(),
        ),
        (
            add_fail_flags(phase_context_factory()),
            pytest.raises(subprocess.CalledProcessError),
        ),
    ],
)
def test_pack_example_algorithm_run(phase_context, context, tmp_path):
    algorithm_dir = generate_example_algorithm(
        context=phase_context,
        output_path=tmp_path,
    )

    with context:
        _test_script(
            script_path=algorithm_dir / "do_test_run.sh",
            extra_arg=f"test-{uuid.uuid4()}",  # Ensure unique build and tests
        )

        output_dir = algorithm_dir / "test" / "output"
        # Check if output is generated (ignore content)
        for output in phase_context["phase"]["algorithm_outputs"]:
            expected_file = output_dir / output["relative_path"]
            assert expected_file.exists()


@pytest.mark.parametrize(
    "phase_context, context",
    [
        (
            phase_context_factory(),
            nullcontext(),
        ),
        (
            add_numerical_slugs(phase_context_factory()),
            nullcontext(),
        ),
        (
            add_fail_flags(phase_context_factory()),
            pytest.raises(subprocess.CalledProcessError),
        ),
    ],
)
def test_pack_example_algorithm_save(phase_context, context, tmp_path):
    script_dir = generate_example_algorithm(
        context=phase_context,
        output_path=tmp_path,
    )

    with context:
        custom_image_tag = _test_save(script_dir=script_dir)

        # Check if saved image exists
        pattern = str(script_dir / f"{custom_image_tag}_*.tar.gz")
        matching_files = glob.glob(pattern)
        assert len(matching_files) == 1, (
            f"Example do_save.sh does not generate the exported "
            f"image matching: {pattern}"
        )


def test_pack_example_evaluation_run_permissions(tmp_path):
    evaluation_dir = generate_example_evaluation(
        context=phase_context_factory(),
        output_path=tmp_path,
    )

    # Run it twice to ensure all permissions are correctly handled
    for _ in range(0, 2):
        _test_script(
            script_path=evaluation_dir / "do_test_run.sh",
            extra_arg=f"test-{uuid.uuid4()}",  # Ensure unique build and tests
        )

        expected_file = evaluation_dir / "test" / "output" / "metrics.json"
        assert expected_file.exists()


@pytest.mark.parametrize(
    "phase_context, context",
    [
        (
            phase_context_factory(),
            nullcontext(),
        ),
        (
            add_numerical_slugs(phase_context_factory()),
            nullcontext(),
        ),
        (
            add_fail_flags(phase_context_factory()),
            pytest.raises(subprocess.CalledProcessError),
        ),
    ],
)
def test_pack_example_evaluation_run(phase_context, context, tmp_path):
    evaluation_dir = generate_example_evaluation(
        context=phase_context,
        output_path=tmp_path,
    )

    with context:
        _test_script(
            script_path=evaluation_dir / "do_test_run.sh",
            extra_arg=f"test-{uuid.uuid4()}",  # Ensure unique build and tests
        )

        expected_file = evaluation_dir / "test" / "output" / "metrics.json"
        assert expected_file.exists()


@pytest.mark.parametrize(
    "phase_context, context",
    [
        (
            phase_context_factory(),
            nullcontext(),
        ),
        (
            add_numerical_slugs(phase_context_factory()),
            nullcontext(),
        ),
        (
            add_fail_flags(phase_context_factory()),
            pytest.raises(subprocess.CalledProcessError),
        ),
    ],
)
def test_pack_example_evaluation_save(phase_context, context, tmp_path):
    script_dir = generate_example_evaluation(
        context=phase_context,
        output_path=tmp_path,
    )

    with context:
        custom_image_tag = _test_save(script_dir=script_dir)

        # Check if saved image exists
        pattern = str(script_dir / f"{custom_image_tag}_*.tar.gz")
        matching_files = glob.glob(pattern)
        assert len(matching_files) == 1, (
            f"Example do_save.sh does not generate the exported "
            f"image matching: {pattern}"
        )
