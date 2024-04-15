import os

import pytest

from grand_challenge_forge.exceptions import OutputOverwriteError
from grand_challenge_forge.forge import generate_challenge_pack
from tests.utils import pack_context_factory


def test_force_overwrites(tmp_path):
    context = pack_context_factory()
    challenge_slug = context["challenge"]["slug"]
    expected_pack = tmp_path / f"{challenge_slug}-challenge-pack"

    assert not expected_pack.exists()  # Sanity

    # First generate the example
    os.mkdir(expected_pack)
    assert expected_pack.exists()

    # Generate should output an error
    with pytest.raises(OutputOverwriteError):
        generate_challenge_pack(context=context, output_directory=tmp_path)

    assert expected_pack.exists()

    # But we can force the issue
    generate_challenge_pack(
        context=context,
        output_directory=tmp_path,
        force=True,
    )
    assert expected_pack.exists()
