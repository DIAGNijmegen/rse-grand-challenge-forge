import pytest

from challenge_forge.exceptions import OutputOverwriteError
from challenge_forge.forge import generate_challenge_pack
from tests.utils import pack_context_factory


def test_force_overwrites(tmp_path):
    context = pack_context_factory()
    # First generate the example
    generate_challenge_pack(context=context, output_directory=tmp_path)

    # Generate again should output an error
    with pytest.raises(OutputOverwriteError):
        generate_challenge_pack(context=context, output_directory=tmp_path)

    # But we can force the issue
    generate_challenge_pack(
        context=context,
        output_directory=tmp_path,
        force=True,
    )
