import logging
import os
import shutil
from pathlib import Path

from cookiecutter.generate import generate_files

from grand_challenge_forge.exceptions import OutputOverwriteError
from grand_challenge_forge.schemas import validate_pack_context
from grand_challenge_forge.utils import cookiecutter_context as cc

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

