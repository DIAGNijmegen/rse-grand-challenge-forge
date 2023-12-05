from unittest.mock import MagicMock, patch

from grand_challenge_forge.exceptions import QualityFailureError
from grand_challenge_forge.utils import (
    change_directory,
    directly_import_module,
)


def upload_to_archive_script(script_dir):
    """Checks if the upload to archive script works as intended"""
    try:
        with change_directory(script_dir):
            gcapi = MagicMock()
            with patch.dict("sys.modules", gcapi=gcapi):
                # Load the script as a module
                upload_files = directly_import_module(
                    name="upload_files",
                    path=script_dir / "upload_files.py",
                )

                # Run the script
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
