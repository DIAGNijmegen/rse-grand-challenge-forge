from contextlib import nullcontext

import pytest

import grand_challenge_forge.quality_control as quality_control
from grand_challenge_forge.exceptions import QualityFailureError
from grand_challenge_forge.forge import (
    generate_challenge_pack,
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


@pytest.mark.parametrize(
    "json_content, condition, num_checks",
    [
        [pack_context_factory(), nullcontext(), 2],
        [BROKEN_UPLOAD_SCRIPT_CONTEXT, pytest.raises(QualityFailureError), 1],
    ],
)
def test_general_pack_quality_assurance(
    json_content, condition, num_checks, tmp_path
):
    checks = []
    generate_challenge_pack(
        context=json_content,
        output_directory=tmp_path,
        quality_control_registry=checks,
    )
    assert len(checks) == num_checks
    with condition:
        for check in checks:
            check()


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
            BROKEN_UPLOAD_SCRIPT_CONTEXT,
            [  # Per phase
                pytest.raises(QualityFailureError),
            ],
        ],
    ],
)
def test_upload_script_quality_check(json_content, conditions, tmp_path):
    for phase, condition in zip(
        json_content["challenge"]["phases"], conditions, strict=True
    ):
        checks = []
        script_dir = generate_upload_to_archive_script(
            context={"phase": phase},
            output_directory=tmp_path,
            quality_control_registry=checks,
        )
        post_creation_hooks(script_dir)
        with condition:
            quality_control.upload_to_archive_script(script_dir)
