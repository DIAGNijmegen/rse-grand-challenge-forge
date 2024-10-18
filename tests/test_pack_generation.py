from grand_challenge_forge.forge import generate_challenge_pack
from tests.utils import pack_context_factory


def test_for_pack_content(tmp_path):
    context = pack_context_factory()
    pack_path = generate_challenge_pack(
        context=context,
        output_path=tmp_path,
    )

    assert (pack_path / "README.md").exists()

    for phase in context["challenge"]["phases"]:
        assert (pack_path / phase["slug"]).exists()

        assert (
            pack_path
            / phase["slug"]
            / f"upload-to-archive-{phase['archive']['slug']}"
        ).exists()

        assert (pack_path / phase["slug"] / "example-algorithm").exists()

        eval_path = pack_path / phase["slug"] / "example-evaluation-method"
        assert eval_path.exists()
        assert (eval_path / "test" / "input" / "predictions.json").exists()
