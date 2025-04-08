from contextlib import nullcontext
from pathlib import Path

import pytest

from grand_challenge_forge.exceptions import InvalidContextError
from grand_challenge_forge.forge import (
    generate_algorithm_template,
    generate_challenge_pack,
)
from tests.utils import (
    algorithm_template_context_factory,
    pack_context_factory,
    zipfile_to_filesystem,
)


@pytest.mark.parametrize(
    "json_context,condition",
    [
        [{}, pytest.raises(InvalidContextError)],
        ["", pytest.raises(InvalidContextError)],
        [{"challenge": []}, pytest.raises(InvalidContextError)],
        [
            {"challenge": {}},
            pytest.raises(InvalidContextError),
        ],
        [
            pack_context_factory(),
            nullcontext(),
        ],
        [
            pack_context_factory(phases=[]),
            nullcontext(),
        ],
    ],
)
def test_pack_context_validity(json_context, condition, tmp_path):
    with condition:
        with zipfile_to_filesystem() as zip_file:
            generate_challenge_pack(
                output_zip_file=zip_file,
                target_zpath=Path(""),
                context=json_context,
            )


@pytest.mark.parametrize(
    "json_context,condition",
    [
        [{}, pytest.raises(InvalidContextError)],
        ["", pytest.raises(InvalidContextError)],
        [{"algorithm": []}, pytest.raises(InvalidContextError)],
        [
            {"algorithm": {}},
            pytest.raises(InvalidContextError),
        ],
        [
            algorithm_template_context_factory(),
            nullcontext(),
        ],
    ],
)
def test_algorithm_template_context_validity(
    json_context, condition, tmp_path
):
    with condition:
        with zipfile_to_filesystem() as zip_file:
            generate_algorithm_template(
                output_zip_file=zip_file,
                target_zpath=Path(""),
                context=json_context,
            )
