import json
import logging
import os
import shutil
from copy import deepcopy
from pathlib import Path

from cookiecutter.generate import generate_files

from grand_challenge_forge.exceptions import OutputOverwriteError
from grand_challenge_forge.schemas import validate_pack_context
from grand_challenge_forge.utils import cookiecutter_context as cc
from grand_challenge_forge.utils import extract_slug, remove_j2_suffix

logger = logging.getLogger(__name__)

SCRIPT_PATH = Path(os.path.dirname(os.path.realpath(__file__)))
PARTIALS_PATH = SCRIPT_PATH / "partials"


def generate_challenge_pack(*, context, output_directory, force=False):
    validate_pack_context(context)

    pack_dir_name = f"{context['challenge']['slug']}-challenge-pack"
    context["pack_dir_name"] = pack_dir_name

    pack_dir = output_directory / pack_dir_name

    _handle_existing(pack_dir, force=force)

    generate_readme(context, output_directory)

    for phase in context["challenge"]["phases"]:
        phase_dir = pack_dir / phase["slug"]
        generate_upload_to_archive_script(
            context={"phase": phase},
            output_directory=phase_dir,
        )

    remove_j2_suffix(pack_dir)

    return pack_dir


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


def generate_upload_to_archive_script(context, output_directory):
    context = deepcopy(context)

    # Cannot use filters in directory names so generate it here
    archive_slug = extract_slug(context["phase"]["archive"]["url"])
    context["phase"]["archive"]["slug"] = archive_slug

    expected_cases, create_files_func = _gen_expected_cases(
        inputs=context["phase"]["inputs"],
        output_directory=output_directory
        / f"upload-to-archive-{archive_slug}",
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


def _gen_expected_cases(inputs, output_directory, n=3):
    to_create_files = []
    result = []
    for i in range(0, n):
        item_files = []
        for j in range(0, len(inputs)):
            item_files.append(
                f"case{i}_file{j}.example"
                if len(inputs) > 1
                else f"file{i}.example"
            )
        to_create_files.extend(item_files)
        result.append(item_files)

    def create_files():
        for filename in to_create_files:
            with open(output_directory / filename, "w") as f:
                f.write("<placeholder data as an example>")

    return [json.dumps(entry) for entry in result], create_files
