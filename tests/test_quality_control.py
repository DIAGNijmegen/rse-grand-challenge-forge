from contextlib import nullcontext

import pytest

import grand_challenge_forge.quality_control as quality_control
from grand_challenge_forge.exceptions import QualityFailureError
from grand_challenge_forge.forge import (
    generate_challenge_pack,
    generate_example_algorithm,
    generate_upload_to_archive_script,
    post_creation_hooks,
)
from tests.utils import pack_context_factory

BROKEN_UPLOAD_SCRIPT_CONTEXT = pack_context_factory(
    phases=[
        {
            **pack_context_factory()["challenge"]["phases"][0],
            "archive": {"url": '"""'},  # This breaks
        }
    ]
)


def test_general_pack_quality_assurance(tmp_path):
    checks = []
    generate_challenge_pack(
        context=pack_context_factory(),
        output_directory=tmp_path,
        quality_control_registry=checks,
    )
    assert len(checks) == 4  # Sanity, ensure the checks are registered


@pytest.mark.slow
@pytest.mark.parametrize(
    "json_content, conditions",
    [
        [
            pack_context_factory(),
            [  # Per phase
                nullcontext(),
                nullcontext(),
            ],
        ],
        [
            pack_context_factory(should_fail=True),
            [  # Per phase
                pytest.raises(QualityFailureError),
                pytest.raises(QualityFailureError),
            ],
        ],
    ],
)
def test_upload_script_quality_check(json_content, conditions, tmp_path):
    for index, (phase, condition) in enumerate(
        zip(json_content["challenge"]["phases"], conditions, strict=True)
    ):
        script_dir = generate_upload_to_archive_script(
            context={"phase": phase},
            output_directory=tmp_path / str(index),
            quality_control_registry=None,
        )
        post_creation_hooks(script_dir)
        with condition:
            quality_control.upload_to_archive_script(script_dir)


@pytest.mark.gpu
@pytest.mark.slow
@pytest.mark.parametrize(
    "json_content, conditions",
    [
        [
            pack_context_factory(),
            [  # Per phase
                nullcontext(),
                nullcontext(),
            ],
        ],
        [
            pack_context_factory(should_fail=True),
            [  # Per phase
                pytest.raises(QualityFailureError),
                pytest.raises(QualityFailureError),
            ],
        ],
    ],
)
def test_example_algorithm_quality_check(json_content, conditions, tmp_path):
    for index, (phase, condition) in enumerate(
        zip(json_content["challenge"]["phases"], conditions, strict=True)
    ):
        algorithm_dir = generate_example_algorithm(
            context={"phase": phase},
            output_directory=tmp_path / str(index),
            quality_control_registry=None,
        )
        post_creation_hooks(algorithm_dir)
        with condition:
            quality_control.example_algorithm(
                phase_context={"phase": phase}, algorithm_dir=algorithm_dir
            )
