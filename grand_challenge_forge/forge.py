import json
import logging
import uuid
from copy import deepcopy
from importlib import metadata
from pathlib import Path

from grand_challenge_forge.generation_utils import (
    copy_and_render,
    generate_socket_value_stub_file,
    socket_to_socket_value,
)
from grand_challenge_forge.schemas import (
    validate_algorithm_template_context,
    validate_pack_context,
)

logger = logging.getLogger(__name__)


def generate_challenge_pack(
    *,
    output_zip_file,
    target_zpath,
    context,
):
    validate_pack_context(context)

    context["grand_challenge_forge_version"] = metadata.version(
        "grand-challenge-forge"
    )

    # Generate the README.md file
    copy_and_render(
        templates_dir_name="pack-readme",
        output_zip_file=output_zip_file,
        target_zpath=target_zpath,
        context=context,
    )

    for phase in context["challenge"]["phases"]:
        phase_zpath = target_zpath / phase["slug"]
        phase_context = {"phase": phase}

        generate_upload_to_archive_script(
            context=phase_context,
            output_zip_file=output_zip_file,
            target_zpath=phase_zpath
            / f"upload-to-archive-{phase['archive']['slug']}",
        )

        generate_example_algorithm(
            context=phase_context,
            output_zip_file=output_zip_file,
            target_zpath=phase_zpath / "example-algorithm",
        )

        generate_example_evaluation(
            context=phase_context,
            output_zip_file=output_zip_file,
            target_zpath=phase_zpath / "example-evaluation-method",
        )


def generate_upload_to_archive_script(
    *,
    output_zip_file,
    target_zpath,
    context,
):
    context = deepcopy(context)

    context["phase"]["expected_cases"] = generate_archive_cases(
        inputs=context["phase"]["algorithm_inputs"],
        output_zip_file=output_zip_file,
        target_zpath=target_zpath,
        number_of_cases=3,
    )

    copy_and_render(
        templates_dir_name="upload-to-archive-script",
        output_zip_file=output_zip_file,
        target_zpath=target_zpath,
        context=context,
    )


def generate_archive_cases(
    *, inputs, output_zip_file, target_zpath, number_of_cases
):
    result = []
    for i in range(0, number_of_cases):
        item_files = []
        for input_socket in inputs:
            zpath = Path(f"case_{i}") / input_socket["relative_path"]

            generate_socket_value_stub_file(
                output_zip_file=output_zip_file,
                target_zpath=target_zpath / zpath,
                socket=input_socket,
            )

            item_files.append(str(zpath))

        result.append(item_files)

    return result


def generate_example_algorithm(*, output_zip_file, target_zpath, context):
    context = deepcopy(context)

    copy_and_render(
        templates_dir_name="example-algorithm",
        output_zip_file=output_zip_file,
        target_zpath=target_zpath,
        context=context,
    )

    # Add .sh files
    copy_and_render(
        templates_dir_name="docker-bash-scripts",
        output_zip_file=output_zip_file,
        target_zpath=target_zpath,
        context={
            "image_tag": f"example-algorithm-{context['phase']['slug']}",
            "tarball_dirname": "model",
            "tarball_extraction_dir": "/opt/ml/model/",
        },
    )

    # Create input files
    input_zdir = target_zpath / "test" / "input"
    for input_ci in context["phase"]["algorithm_inputs"]:
        generate_socket_value_stub_file(
            output_zip_file=output_zip_file,
            target_zpath=input_zdir / input_ci["relative_path"],
            socket=input_ci,
        )

    return target_zpath


def generate_example_evaluation(*, output_zip_file, target_zpath, context):
    copy_and_render(
        templates_dir_name="example-evaluation-method",
        output_zip_file=output_zip_file,
        target_zpath=target_zpath,
        context=context,
    )

    # Add .sh files
    copy_and_render(
        templates_dir_name="docker-bash-scripts",
        output_zip_file=output_zip_file,
        target_zpath=target_zpath,
        context={
            "image_tag": f"example-evaluation-{context['phase']['slug']}",
            "tarball_dirname": "ground_truth",
            "tarball_extraction_dir": "/opt/ml/input/data/ground_truth/",
        },
    )

    generate_predictions(
        output_zip_file=output_zip_file,
        target_zpath=target_zpath / "test" / "input",
        context=context,
        number_of_jobs=3,
    )


def generate_predictions(
    *,
    output_zip_file,
    target_zpath,
    context,
    number_of_jobs,
):
    predictions = []
    for _ in range(0, number_of_jobs):
        predictions.append(
            {
                "pk": str(uuid.uuid4()),
                "inputs": [
                    socket_to_socket_value(socket)
                    for socket in context["phase"]["algorithm_inputs"]
                ],
                "outputs": [
                    socket_to_socket_value(socket)
                    for socket in context["phase"]["algorithm_outputs"]
                ],
                "status": "Succeeded",
                "started_at": "2024-11-29T10:31:25.691799Z",
                "completed_at": "2024-11-29T10:31:50.691799Z",
            }
        )

    output_zip_file.writestr(
        str(target_zpath / "predictions.json"),
        json.dumps(predictions, indent=4),
    )

    for prediction in predictions:
        prediction_zpath = target_zpath / prediction["pk"]
        for socket_value in prediction["outputs"]:
            generate_socket_value_stub_file(
                output_zip_file=output_zip_file,
                target_zpath=prediction_zpath
                / "output"
                / socket_value["interface"]["relative_path"],
                socket=socket_value["interface"],
            )


def generate_algorithm_template(
    *,
    context,
    output_zip_file,
    target_zpath,
):
    validate_algorithm_template_context(context)

    context["grand_challenge_forge_version"] = metadata.version(
        "grand-challenge-forge"
    )

    copy_and_render(
        templates_dir_name="algorithm-template",
        output_zip_file=output_zip_file,
        target_zpath=target_zpath,
        context=context,
    )

    # Create input files
    input_dir = target_zpath / "test" / "input"
    for input_ci in context["algorithm"]["inputs"]:
        generate_socket_value_stub_file(
            output_zip_file=output_zip_file,
            target_zpath=input_dir / input_ci["relative_path"],
            socket=input_ci,
        )

    # Add .sh files
    copy_and_render(
        templates_dir_name="docker-bash-scripts",
        output_zip_file=output_zip_file,
        target_zpath=target_zpath,
        context={
            "image_tag": context["algorithm"]["slug"],
            "tarball_dirname": "model",
            "tarball_extraction_dir": "/opt/ml/model/",
        },
    )
