import json
import logging
from importlib import metadata
from pathlib import Path

import click

from challenge_forge import logger
from challenge_forge.exceptions import ChallengeForgeError
from challenge_forge.forge import generate_challenge_pack
from challenge_forge.utils import truncate_with_epsilons


@click.command()
@click.version_option(metadata.version("challenge-forge"), "-v", "--version")
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Sets verbosity level. Stacks (e.g. -vv = debug)",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(
        exists=False,
        file_okay=False,
        dir_okay=True,
        readable=True,
        writable=True,
        resolve_path=True,
    ),
    default="dist/",
    show_default=True,
)
@click.option(
    "-f",
    "--force",
    is_flag=True,
    default=False,
)
@click.argument(
    "contexts",
    nargs=-1,
)
def cli(output, force, contexts, verbose=0):
    """
    Generates a challenge pack using context

    A context can be a filename or a JSON string.

    Multiple contexts can be provided. Each will be processed independently.
    """
    output_dir = Path(output)

    ch = logging.StreamHandler()

    if verbose == 0:
        logger.setLevel(logging.WARNING)
        ch.setLevel(logging.WARNING)
    elif verbose == 1:
        logger.setLevel(logging.INFO)
        ch.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.DEBUG)
        ch.setLevel(logging.DEBUG)

    for context in contexts:
        resolved_context = _resolve_context(src=context)
        if resolved_context:
            try:
                generate_challenge_pack(
                    context=resolved_context,
                    output_directory=output_dir,
                    force=force,
                )
            except Exception as e:
                if isinstance(e, ChallengeForgeError):
                    logger.error(e)
                else:
                    raise e


def _resolve_context(src):
    try:
        if (p := Path(src)).exists() and p.is_file():
            return _read_json_file(p)
        return json.loads(src)
    except json.decoder.JSONDecodeError as e:
        logger.error(
            f"Could not resolve context source:\n"
            f"'{truncate_with_epsilons(src)!r}' {e}"
        )


def _read_json_file(json_file):
    with open(json_file, "r") as f:
        context = json.load(f)
    return context
