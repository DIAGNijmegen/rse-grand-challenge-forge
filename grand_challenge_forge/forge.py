import json
import logging
import shutil
import uuid
from copy import deepcopy
from importlib import metadata
from pathlib import Path

import grand_challenge_forge.quality_control as qc
from grand_challenge_forge.exceptions import OutputOverwriteError
from grand_challenge_forge.generation_utils import (
    ci_to_civ,
    copy_and_render,
    create_civ_stub_file,
)
from grand_challenge_forge.schemas import validate_pack_context

logger = logging.getLogger(__name__)


def generate_challenge_pack(
    *,
    context,
    output_path,
    quality_control_registry=None,
    force=False,
):
    validate_pack_context(context)

    context["grand_challenge_forge_version"] = metadata.version(
        "grand-challenge-forge"
    )

    pack_path = output_path / f"{context['challenge']['slug']}-challenge-pack"

    if pack_path.exists():
        _handle_existing(pack_path, force=force)

    generate_readme(context=context, output_path=pack_path)

    for phase in context["challenge"]["phases"]:
        phase_path = pack_path / phase["slug"]
        phase_context = {"phase": phase}

        generate_upload_to_archive_script(
            context=phase_context,
            output_path=phase_path,
            quality_control_registry=quality_control_registry,
        )

        generate_example_algorithm(
            context=phase_context,
            output_path=phase_path,
            quality_control_registry=quality_control_registry,
        )

        generate_example_evaluation(
            context=phase_context,
            output_path=phase_path,
            quality_control_registry=quality_control_registry,
        )

    return pack_path


def _handle_existing(directory, force):
    if force:
        shutil.rmtree(directory)
    else:
        raise OutputOverwriteError(
            f"{directory} already exists! Use force to overwrite"
        )


def generate_readme(*, context, output_path):
    copy_and_render(
        templates_dir_name="pack-readme",
        output_path=output_path,
        context=context,
    )


def generate_upload_to_archive_script(
    *, context, output_path, quality_control_registry=None
):
    context = deepcopy(context)

    script_path = (
        output_path
        / f"upload-to-archive-{context['phase']['archive']['slug']}"
    )

    # Map the expected case, but only create after the script
    expected_cases, create_files_func = _gen_expected_archive_cases(
        inputs=context["phase"]["algorithm_inputs"],
        output_path=script_path,
    )
    context["phase"]["expected_cases"] = expected_cases

    copy_and_render(
        templates_dir_name="upload-to-archive-script",
        output_path=script_path,
        context=context,
    )

    create_files_func()

    def quality_check():
        qc.upload_to_archive_script(script_path=script_path)

    if quality_control_registry is not None:
        quality_control_registry.append(quality_check)

    return script_path


def _gen_expected_archive_cases(inputs, output_path, n=3):
    to_create_files = []
    result = []
    for i in range(0, n):
        item_files = []
        for j in range(0, len(inputs)):
            item_files.append(
                f"case{i}/file{j}.example"
                if len(inputs) > 1
                else f"file{i}.example"
            )
        to_create_files.extend(item_files)
        result.append(item_files)

    def create_files():
        for filename in to_create_files:
            filepath = output_path / Path(filename)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, "w") as f:
                f.write('"This is just placeholder data, move along!>"')

    return [json.dumps(entry) for entry in result], create_files


def generate_example_algorithm(
    *, context, output_path, quality_control_registry=None
):
    algorithm_path = output_path / "example-algorithm"

    context["_no_gpus"] = context.get("_no_gpus", False)

    copy_and_render(
        templates_dir_name="example-algorithm",
        output_path=algorithm_path,
        context=context,
    )

    # Create input files
    input_dir = algorithm_path / "test" / "input"
    for input_ci in context["phase"]["algorithm_inputs"]:
        create_civ_stub_file(
            target_path=input_dir / input_ci["relative_path"],
            component_interface=input_ci,
        )

    def quality_check():
        qc.example_algorithm(
            phase_context=context, algorithm_dir=algorithm_path
        )

    if quality_control_registry is not None:
        quality_control_registry.append(quality_check)

    return algorithm_path


def generate_example_evaluation(
    context, output_path, quality_control_registry=None
):
    evaluation_path = output_path / "example-evaluation-method"

    context["_no_gpus"] = context.get("_no_gpus", False)

    copy_and_render(
        templates_dir_name="example-evaluation-method",
        output_path=evaluation_path,
        context=context,
    )

    generate_predictions(context, evaluation_path)

    def quality_check():
        qc.example_evaluation(
            phase_context=context, evaluation_dir=evaluation_path
        )

    if quality_control_registry is not None:
        quality_control_registry.append(quality_check)

    return evaluation_path


def generate_predictions(context, evaluation_path, n=3):
    input_dir = evaluation_path / "test" / "input"
    input_dir.mkdir(parents=True, exist_ok=True)

    predictions = []
    for _ in range(0, n):
        predictions.append(
            {
                "pk": str(uuid.uuid4()),
                "inputs": [
                    ci_to_civ(ci)
                    for ci in context["phase"]["algorithm_inputs"]
                ],
                "outputs": [
                    ci_to_civ(ci)
                    for ci in context["phase"]["algorithm_outputs"]
                ],
                "status": "Succeeded",
                "started_at": "2024-11-29T10:31:25.691799Z",
                "completed_at": "2024-11-29T10:31:50.691799Z",
            }
        )
    with open(input_dir / "predictions.json", "w") as f:
        f.write(json.dumps(predictions, indent=4))

    for prediction in predictions:
        for civ in prediction["outputs"]:
            job_path = (
                input_dir
                / prediction["pk"]
                / "output"
                / civ["interface"]["relative_path"]
            )
            job_path.parent.mkdir(parents=True, exist_ok=True)
            create_civ_stub_file(
                target_path=job_path,
                component_interface=civ["interface"],
            )
