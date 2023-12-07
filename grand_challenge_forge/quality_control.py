import logging
import subprocess
import sys
from unittest.mock import MagicMock, patch

from grand_challenge_forge.exceptions import QualityFailureError
from grand_challenge_forge.utils import (
    change_directory,
    directly_import_module,
)

logger = logging.getLogger(__name__)


def upload_to_archive_script(script_dir):
    """Checks if the upload to archive script works as intended"""
    logger.debug(f"Quality check over script in: {script_dir.stem}")

    try:
        with change_directory(script_dir):
            gcapi = MagicMock()
            with patch.dict("sys.modules", gcapi=gcapi):
                # Load the script as a module
                upload_files = directly_import_module(
                    name="upload_files",
                    path=script_dir / "upload_files.py",
                )

                # Run the script, but noop print
                with patch("builtins.print"):
                    upload_files.main()

            # Assert that it reaches out via gcapi
            try:
                gcapi.Client.assert_called()
                gcapi.Client().archive_items.create.assert_called()
                gcapi.Client().update_archive_item.assert_called()
            except AssertionError as e:
                raise QualityFailureError(
                    f"Upload script does not contact grand-challenge. {e}"
                ) from e
    except (FileNotFoundError, SyntaxError) as e:
        raise QualityFailureError(
            f"Upload script does not seem to exist or is not valid: {e}"
        ) from e
    logger.debug("Quality OK!")


def example_algorithm(phase_context, algorithm_dir):
    """Checks if the example algorithm works as intended"""
    logger.debug(f"Quality check over algorithm in: {algorithm_dir}")

    result = subprocess.run(
        [algorithm_dir / "run_test.sh"],
        capture_output=True,
    )

    output_dir = algorithm_dir / "test" / "output"

    report_output = (
        f"stdin:\n"
        f"{result.stdout.decode(sys.getfilesystemencoding())}"
        f"stderr:\n"
        f"{result.stderr.decode(sys.getfilesystemencoding())}"
    )

    if result.returncode != 0:  # Not a clean exit
        raise QualityFailureError(
            f"Example algorithm in {algorithm_dir!r} does not exit with 0:\n"
            f"{report_output}"
        )
    elif result.stderr:
        raise QualityFailureError(
            f"Example algorithm in {algorithm_dir!r} produces errors:\n"
            f"{report_output}"
        )

    # Check if output is generated (ignore content)
    for output in phase_context["phase"]["outputs"]:
        expected_file = output_dir / output["relative_path"]
        if not expected_file.exists():
            raise QualityFailureError(
                "Example algorithm does not generate output: "
                f"{output['relative_path']}"
            )

    logger.debug("Quality OK!")
