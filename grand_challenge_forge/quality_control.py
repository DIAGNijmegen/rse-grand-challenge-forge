import importlib
from unittest.mock import MagicMock, Mock, patch

from grand_challenge_forge.exceptions import QualityFailureError
from grand_challenge_forge.utils import change_directory


def upload_to_archive_script(script_dir):
    """Quality assurance over the upload script, ensures that the script works"""
    try:
        with change_directory(script_dir):
            gcapi = _generate_mock_gcapi()
            with patch.dict("sys.modules", gcapi=gcapi):
                upload_files = _directly_import_module(
                    name="upload_files",
                    path=script_dir / "upload_files.py",
                )
                upload_files.main()

            # Assert that reaches out via gcapi
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


def _directly_import_module(name, path):
    assert path.exists()
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def _generate_mock_gcapi():
    gcapi = MagicMock()
    gcapi.Client().archives.detail = Mock(
        return_value={
            "api_url": "an api url",
            "title": "an archive title",
        }
    )
    gcapi.Client().archive_items.create = Mock(
        return_value={
            "pk": "A primary key",
        }
    )
    return gcapi
