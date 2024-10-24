from grand_challenge_forge.forge import generate_algorithm_template
from tests.utils import algorithm_template_context_factory


def test_for_algorithm_template_content(tmp_path):
    context = algorithm_template_context_factory()
    template_path = generate_algorithm_template(
        context=context,
        output_path=tmp_path,
    )

    for filename in [
        "Dockerfile",
        "README.md",
        "resources",
        "inference.py",
        "requirements.txt",
        "do_build.sh",
        "do_save.sh",
        "do_test_run.sh",
    ]:
        assert (template_path / filename).exists()
