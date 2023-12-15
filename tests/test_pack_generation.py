from grand_challenge_forge.forge import generate_challenge_pack
from grand_challenge_forge.generation_utils import extract_slug
from tests.utils import pack_context_factory


def test_for_pack_content(tmp_path):
    context = pack_context_factory()
    pack_dir = generate_challenge_pack(
        context=context,
        output_directory=tmp_path,
    )

    assert (pack_dir / "README.md").exists

    for phase in context["challenge"]["phases"]:
        assert (pack_dir / phase["slug"]).exists

        assert (pack_dir / phase["slug"] / "example-algorithm").exists

        eval_dir = pack_dir / phase["slug"] / "example-evaluation-method"
        assert eval_dir.exists
        assert (eval_dir / "test" / "input" / "prediction.json").exists

        assert (
            pack_dir
            / phase["slug"]
            / f"upload-to-archive-{extract_slug(phase['archive']['url'])}"
        ).exists
