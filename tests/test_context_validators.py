from contextlib import nullcontext

import pytest

from grand_challenge_forge.exceptions import InvalidContextError
from grand_challenge_forge.forge import generate_challenge_pack
from tests.utils import pack_context_factory


@pytest.mark.parametrize(
    "json_context,condition",
    [
        [{}, pytest.raises(InvalidContextError)],
        ["", pytest.raises(InvalidContextError)],
        [{"challenge": []}, pytest.raises(InvalidContextError)],
        [{}, pytest.raises(InvalidContextError)],
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
def test_context_validity(json_context, condition, tmp_path):
    with condition:
        generate_challenge_pack(context=json_context, output_path=tmp_path)
