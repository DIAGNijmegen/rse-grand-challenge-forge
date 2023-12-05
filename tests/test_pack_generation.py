from grand_challenge_forge.forge import generate_challenge_pack
from tests.utils import pack_context_factory


def test_pack_readme(tmp_path):
    pack_dir = generate_challenge_pack(
        context=pack_context_factory(),
        output_directory=tmp_path,
    )

    assert (pack_dir / "README.md").exists
