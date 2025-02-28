from contextlib import nullcontext

import pytest

import grand_challenge_forge.quality_control as quality_control
from grand_challenge_forge.exceptions import QualityFailureError
from grand_challenge_forge.forge import (
    generate_algorithm_template,
    generate_challenge_pack,
    generate_example_algorithm,
    generate_example_evaluation,
    generate_upload_to_archive_script,
)
from tests.utils import (
    algorithm_template_context_factory,
    numerical_pack_context_factory,
    pack_context_factory,
)

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
        output_path=tmp_path,
        quality_control_registry=checks,
    )
    assert len(checks) == 6  # Sanity, ensure the checks are registered


def test_general_algorithm_template_quality_assurance(tmp_path):
    checks = []
    generate_algorithm_template(
        context=algorithm_template_context_factory(),
        output_path=tmp_path,
        quality_control_registry=checks,
    )
    assert len(checks) == 1  # Sanity, ensure the checks are registered


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
            numerical_pack_context_factory(),
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
            output_path=tmp_path / str(index),
            quality_control_registry=None,
        )
        with condition:
            quality_control.upload_to_archive_script(script_dir)


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
            numerical_pack_context_factory(),
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
            context={
                "phase": phase,
                # Debug purposes, so we don't need to run with a gpu:
                "_no_gpus": True,
            },
            output_path=tmp_path / str(index),
            quality_control_registry=None,
        )
        with condition:
            quality_control.example_algorithm(
                phase_context={"phase": phase}, algorithm_dir=algorithm_dir
            )


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
            numerical_pack_context_factory(),
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
def test_example_evaluation_quality_check(json_content, conditions, tmp_path):
    for index, (phase, condition) in enumerate(
        zip(json_content["challenge"]["phases"], conditions, strict=True)
    ):
        evaluation_dir = generate_example_evaluation(
            context={
                "phase": phase,
                # Debug purposes, so we don't need to run with a gpu:
                "_no_gpus": True,
            },
            output_path=tmp_path / str(index),
            quality_control_registry=None,
        )
        with condition:
            quality_control.example_evaluation(
                phase_context={"phase": phase}, evaluation_dir=evaluation_dir
            )


@pytest.mark.slow
@pytest.mark.parametrize(
    "json_content, condition",
    [
        [
            algorithm_template_context_factory(),
            nullcontext(),
        ],
        [
            algorithm_template_context_factory(should_fail=True),
            pytest.raises(QualityFailureError),
        ],
    ],
)
def test_algorithm_template_quality_check(json_content, condition, tmp_path):
    json_content.update(
        {
            "_no_gpus": True,  # Debug purposes, so we don't need to run with a gpu
        }
    )

    path = generate_algorithm_template(
        context=json_content,
        output_path=tmp_path,
        quality_control_registry=None,
    )
    with condition:
        quality_control.algorithm_template(
            algorithm_context=json_content, algorithm_template_path=path
        )
