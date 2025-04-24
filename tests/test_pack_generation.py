import glob
import json
from unittest.mock import MagicMock, patch

import pytest

from grand_challenge_forge.forge import (
    generate_challenge_pack,
    generate_example_algorithm,
    generate_example_evaluation,
    generate_upload_to_archive_script,
)
from grand_challenge_forge.generation_utils import zipfile_to_filesystem
from grand_challenge_forge.utils import (
    change_directory,
    directly_import_module,
)
from tests.utils import (
    _test_script_run,
    add_numerical_slugs,
    mocked_binaries,
    pack_context_factory,
    phase_context_factory,
)


def test_for_pack_content(tmp_path, testrun_zpath):
    context = pack_context_factory()

    with zipfile_to_filesystem(output_path=tmp_path) as zip_file:
        generate_challenge_pack(
            output_zip_file=zip_file,
            target_zpath=testrun_zpath,
            context=context,
        )

    pack_path = tmp_path / testrun_zpath

    assert (pack_path / "README.md").exists()

    for phase in context["challenge"]["phases"]:
        assert (pack_path / phase["slug"]).exists()

        assert (
            pack_path
            / phase["slug"]
            / f"upload-to-archive-{phase['archive']['slug']}"
        ).exists()

        assert (pack_path / phase["slug"] / "example-algorithm").exists()
        for idx, interface in enumerate(phase["algorithm_interfaces"]):
            for input in interface["inputs"]:
                expected_file = (
                    pack_path
                    / phase["slug"]
                    / "example-algorithm"
                    / "test"
                    / "input"
                    / f"interface_{idx}"
                    / input["relative_path"]
                )
                assert expected_file.exists()

        eval_path = pack_path / phase["slug"] / "example-evaluation-method"
        assert eval_path.exists()
        eval_input_path = eval_path / "test" / "input"
        assert (eval_input_path / "predictions.json").exists()
        for input in phase["evaluation_additional_inputs"]:
            expected_file = eval_input_path / input["relative_path"]
            assert expected_file.exists()


@pytest.mark.parametrize(
    "phase_context",
    [
        phase_context_factory(),
        add_numerical_slugs(phase_context_factory()),
    ],
)
def test_pack_upload_to_archive_script(phase_context, tmp_path, testrun_zpath):
    """Checks if the upload to archive script works as intended"""

    with zipfile_to_filesystem(output_path=tmp_path) as zip_file:
        generate_upload_to_archive_script(
            output_zip_file=zip_file,
            target_zpath=testrun_zpath,
            context=phase_context,
        )

    script_dir = tmp_path / testrun_zpath

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
        assert gcapi.Client.call_count == 1

        # Two interface, each with 3 cases
        assert gcapi.Client().archive_items.create.call_count == 6
        assert gcapi.Client().update_archive_item.call_count == 6


def test_pack_example_algorithm_run_permissions(tmp_path, testrun_zpath):
    phase_context = phase_context_factory()

    with zipfile_to_filesystem(output_path=tmp_path) as zip_file:
        generate_example_algorithm(
            context=phase_context,
            output_zip_file=zip_file,
            target_zpath=testrun_zpath,
        )

    algorithm_path = tmp_path / testrun_zpath

    # Run it twice to ensure all permissions are correctly handled
    for _ in range(0, 2):
        _test_script_run(script_path=algorithm_path / "do_test_run.sh")


@pytest.mark.parametrize(
    "phase_context",
    [
        phase_context_factory(),
        add_numerical_slugs(phase_context_factory()),
    ],
)
def test_pack_example_algorithm_run(phase_context, tmp_path, testrun_zpath):
    with zipfile_to_filesystem(output_path=tmp_path) as zip_file:
        generate_example_algorithm(
            context=phase_context,
            output_zip_file=zip_file,
            target_zpath=testrun_zpath,
        )

    algorithm_path = tmp_path / testrun_zpath

    _test_script_run(script_path=algorithm_path / "do_test_run.sh")

    for idx, interface in enumerate(
        phase_context["phase"]["algorithm_interfaces"]
    ):
        output_dir = algorithm_path / "test" / "output" / f"interface_{idx}"
        # Check if output is generated
        for output in interface["outputs"]:
            expected_file = output_dir / output["relative_path"]
            assert expected_file.exists()


def test_pack_example_algorithm_save(tmp_path, testrun_zpath):
    phase_context = phase_context_factory()

    with zipfile_to_filesystem(output_path=tmp_path) as zip_file:
        generate_example_algorithm(
            context=phase_context,
            output_zip_file=zip_file,
            target_zpath=testrun_zpath,
        )

    algorithm_path = tmp_path / testrun_zpath

    with mocked_binaries():
        _test_script_run(script_path=algorithm_path / "do_save.sh")

    # Check if saved image exists
    tar_filename = f"example-algorithm-{phase_context['phase']['slug']}"
    pattern = str(algorithm_path / f"{tar_filename}_*.tar.gz")
    matching_files = glob.glob(pattern)
    assert len(matching_files) == 1, (
        f"Example do_save.sh does not generate the exported "
        f"image matching: {pattern}"
    )


def test_pack_example_evaluation_run_permissions(tmp_path, testrun_zpath):
    with zipfile_to_filesystem(output_path=tmp_path) as zip_file:
        generate_example_evaluation(
            context=phase_context_factory(),
            output_zip_file=zip_file,
            target_zpath=testrun_zpath,
        )

    evaluation_path = tmp_path / testrun_zpath

    # Run it twice to ensure all permissions are correctly handled
    for _ in range(0, 2):
        _test_script_run(script_path=evaluation_path / "do_test_run.sh")


@pytest.mark.parametrize(
    "phase_context, num_metrics",
    (
        (
            phase_context_factory(),
            6,
        ),
        (
            add_numerical_slugs(phase_context_factory()),
            6,
        ),
        # Just the algorithm interfaces
        (
            phase_context_factory(
                evaluation_additional_inputs=[],
                evaluation_additional_outputs=[],
            ),
            6,
        ),
        # Just the evaluation additional outputs
        (
            phase_context_factory(
                algorithm_interfaces=[],
                evaluation_additional_inputs=[],
            ),
            0,
        ),
        # Just the evaluation additional inputs
        (
            phase_context_factory(
                algorithm_interfaces=[],
                evaluation_additional_outputs=[],
            ),
            0,
        ),
    ),
)
def test_pack_example_evaluation_run(
    phase_context, num_metrics, tmp_path, testrun_zpath
):
    with zipfile_to_filesystem(output_path=tmp_path) as zip_file:
        generate_example_evaluation(
            context=phase_context,
            output_zip_file=zip_file,
            target_zpath=testrun_zpath,
        )

    evaluation_path = tmp_path / testrun_zpath
    output_dir = evaluation_path / "test" / "output"
    metrics_file = evaluation_path / "test" / "output" / "metrics.json"

    # Sanity
    assert not metrics_file.exists()
    for output in phase_context["phase"]["evaluation_additional_outputs"]:
        expected_file = output_dir / output["relative_path"]
        assert not expected_file.exists()

    _test_script_run(script_path=evaluation_path / "do_test_run.sh")

    assert metrics_file.exists()

    # Read and validate the contents of the generated metrics.json file
    with open(metrics_file, "r") as f:
        metrics_data = json.load(f)
    assert len(metrics_data["results"]) == num_metrics

    # Check if the additional outputs are generated
    for output in phase_context["phase"]["evaluation_additional_outputs"]:
        expected_file = output_dir / output["relative_path"]
        assert expected_file.exists()


def test_pack_example_evaluation_save(tmp_path, testrun_zpath):
    phase_context = phase_context_factory()
    with zipfile_to_filesystem(output_path=tmp_path) as zip_file:
        generate_example_evaluation(
            context=phase_context,
            output_zip_file=zip_file,
            target_zpath=testrun_zpath,
        )

    evaluation_path = tmp_path / testrun_zpath

    with mocked_binaries():
        _test_script_run(script_path=evaluation_path / "do_save.sh")

    # Check if saved image exists
    tar_filename = f"example-evaluation-{phase_context['phase']['slug']}"
    pattern = str(evaluation_path / f"{tar_filename}_*.tar.gz")
    matching_files = glob.glob(pattern)
    assert len(matching_files) == 1, (
        f"Example do_save.sh does not generate the exported "
        f"image matching: {pattern}"
    )
