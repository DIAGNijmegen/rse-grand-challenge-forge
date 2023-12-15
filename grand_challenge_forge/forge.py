import json
import logging
import os
import shutil
import uuid
from copy import deepcopy
from pathlib import Path

from cookiecutter.generate import generate_files

import grand_challenge_forge.quality_control as qc
from grand_challenge_forge.exceptions import OutputOverwriteError
from grand_challenge_forge.generation_utils import (
    ci_to_civ,
    create_civ_stub_file,
    extract_slug,
)
from grand_challenge_forge.schemas import validate_pack_context
from grand_challenge_forge.utils import cookiecutter_context as cc
from grand_challenge_forge.utils import remove_j2_suffix

logger = logging.getLogger(__name__)

SCRIPT_PATH = Path(os.path.dirname(os.path.realpath(__file__)))
PARTIALS_PATH = SCRIPT_PATH / "partials"
RESOURCES_PATH = SCRIPT_PATH / "resources"


def generate_challenge_pack(
    *,
    context,
    output_directory,
    quality_control_registry=None,
    force=False,
):
    validate_pack_context(context)

    pack_dir_name = f"{context['challenge']['slug']}-challenge-pack"
    context["pack_dir_name"] = pack_dir_name

    pack_dir = output_directory / pack_dir_name

    _handle_existing(pack_dir, force=force)

    generate_readme(context, output_directory)

    for phase in context["challenge"]["phases"]:
        phase_dir = pack_dir / phase["slug"]
        phase_context = {"phase": phase}

        generate_upload_to_archive_script(
            context=phase_context,
            output_directory=phase_dir,
            quality_control_registry=quality_control_registry,
        )

        generate_example_algorithm(
            context=phase_context,
            output_directory=phase_dir,
            quality_control_registry=quality_control_registry,
        )

        generate_example_evaluation(
            context=phase_context,
            output_directory=phase_dir,
            quality_control_registry=quality_control_registry,
        )

    post_creation_hooks(pack_dir)

    return pack_dir


def post_creation_hooks(pack_dir):
    remove_j2_suffix(pack_dir)


def _handle_existing(directory, force):
    if directory.exists():
        if force:
            shutil.rmtree(directory)
        else:
            raise OutputOverwriteError(
                f"{directory} already exists! Use force to overwrite"
            )


def generate_readme(context, output_directory):
    generate_files(
        repo_dir=PARTIALS_PATH / "pack-readme",
        context=cc(context),
        overwrite_if_exists=False,
        skip_if_file_exists=False,
        output_dir=output_directory,
    )


def generate_upload_to_archive_script(
    context, output_directory, quality_control_registry=None
):
    context = deepcopy(context)

    # Cannot always use filters in directory names so generate it here
    context["phase"]["archive"]["slug"] = extract_slug(
        context["phase"]["archive"]["url"]
    )

    script_dir = (
        output_directory
        / f"upload-to-archive-{context['phase']['archive']['slug']}"
    )

    # Map the expected case, but only create after the script
    expected_cases, create_files_func = _gen_expected_archive_cases(
        inputs=context["phase"]["inputs"],
        output_directory=script_dir,
    )
    context["phase"]["expected_cases"] = expected_cases

    generate_files(
        repo_dir=PARTIALS_PATH / "upload-to-archive-script",
        context=cc(context),
        overwrite_if_exists=False,
        skip_if_file_exists=False,
        output_dir=output_directory,
    )

    create_files_func()

    def quality_check():
        qc.upload_to_archive_script(script_dir=script_dir)

    if quality_control_registry is not None:
        quality_control_registry.append(quality_check)

    return script_dir


def _gen_expected_archive_cases(inputs, output_directory, n=3):
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
            filepath = output_directory / Path(filename)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, "w") as f:
                f.write('"This is just placeholder data, move along!>"')

    return [json.dumps(entry) for entry in result], create_files


def generate_example_algorithm(
    context, output_directory, quality_control_registry=None
):
    algorithm_dir = generate_files(
        repo_dir=PARTIALS_PATH / "example-algorithm",
        context=cc(context),
        overwrite_if_exists=False,
        skip_if_file_exists=False,
        output_dir=output_directory,
    )

    algorithm_dir = Path(algorithm_dir)

    # Create input files
    input_dir = algorithm_dir / "test" / "input"
    for input_ci in context["phase"]["inputs"]:
        create_civ_stub_file(
            target_dir=input_dir / input_ci["relative_path"],
            component_interface=input_ci,
        )

    def quality_check():
        qc.example_algorithm(
            phase_context=context, algorithm_dir=algorithm_dir
        )

    if quality_control_registry is not None:
        quality_control_registry.append(quality_check)

    return algorithm_dir


def generate_example_evaluation(
    context, output_directory, quality_control_registry=None
):
    evaluation_dir = generate_files(
        repo_dir=PARTIALS_PATH / "example-evaluation-method",
        context=cc(context),
        overwrite_if_exists=False,
        skip_if_file_exists=False,
        output_dir=output_directory,
    )

    evaluation_dir = Path(evaluation_dir)

    generate_predictions(context, evaluation_dir)

    def quality_check():
        qc.example_evaluation(
            phase_context=context, evaluation_dir=evaluation_dir
        )

    if quality_control_registry is not None:
        quality_control_registry.append(quality_check)

    return evaluation_dir


def generate_predictions(context, evaluation_dir, n=3):
    input_dir = evaluation_dir / "test" / "input"
    input_dir.mkdir(parents=True, exist_ok=True)

    predictions = []
    for _ in range(0, n):
        predictions.append(
            {
                "pk": str(uuid.uuid4()),
                "inputs": [ci_to_civ(ci) for ci in context["phase"]["inputs"]],
                "outputs": [
                    ci_to_civ(ci) for ci in context["phase"]["outputs"]
                ],
                "status": "Succeeded",
                "started_at": "2023-11-29T10:31:25.691799Z",
                "completed_at": "2023-11-29T10:31:50.691799Z",
            }
        )
    with open(input_dir / "predictions.json", "w") as f:
        f.write(json.dumps(predictions, indent=4))

    for prediction in predictions:
        for civ in prediction["outputs"]:
            job_dir = (
                input_dir
                / prediction["pk"]
                / "output"
                / civ["interface"]["relative_path"]
            )
            job_dir.parent.mkdir(parents=True, exist_ok=True)
            create_civ_stub_file(
                target_dir=job_dir,
                component_interface=civ["interface"],
            )
