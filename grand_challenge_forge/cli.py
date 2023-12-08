import json
import logging
from importlib import metadata
from pathlib import Path

import click

from grand_challenge_forge import logger
from grand_challenge_forge.exceptions import ChallengeForgeError
from grand_challenge_forge.forge import generate_challenge_pack
from grand_challenge_forge.utils import truncate_with_epsilons


@click.command()
@click.version_option(metadata.version("grand-challenge-forge"), "--version")
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
@click.option(
    "-n",
    "--no-quality-control",
    is_flag=True,
    default=False,
)
@click.argument(
    "contexts",
    nargs=-1,
)
def cli(output, force, contexts, no_quality_control, verbose=0):
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

    for index, context in enumerate(contexts):
        resolved_context = _resolve_context(src=context)
        if resolved_context:
            try:
                quality_control_registry = None if no_quality_control else []
                logger.info(
                    f"🏗️Started working on pack [{index + 1} of {len(contexts)}]"
                )
                pack_dir = generate_challenge_pack(
                    context=resolved_context,
                    output_directory=output_dir,
                    force=force,
                    quality_control_registry=quality_control_registry,
                )
                logger.info(f"🎒 Created Pack {pack_dir.stem!r}")
                if quality_control_registry:
                    logger.info("👷 Starting quality checks...")
                    for check in quality_control_registry:
                        check()
                    logger.info("✅  Quality checks complete!")
                logger.info(f"📢 Pack is here: {pack_dir}")
            except Exception as e:
                if isinstance(e, ChallengeForgeError):
                    logger.error(f"💔 {e}")
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
