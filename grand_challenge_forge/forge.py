import logging
import os
import shutil

from grand_challenge_forge.exceptions import OutputOverwriteError
from grand_challenge_forge.schemas import validate_pack_context

logger = logging.getLogger(__name__)


def generate_challenge_pack(*, context, output_directory, force=False):
    validate_pack_context(context)

    pack_name = f"{context['challenge']['slug']}-challenge-pack"
    context["pack_name"] = pack_name

    pack_dir = output_directory / pack_name

    _create_dir(pack_dir, force=force)


def _create_dir(directory, force):
    if directory.exists():
        if force:
            shutil.rmtree(directory)
        else:
            raise OutputOverwriteError(
                f"{directory} already exists! Use force to overwrite"
            )
    os.makedirs(directory)
