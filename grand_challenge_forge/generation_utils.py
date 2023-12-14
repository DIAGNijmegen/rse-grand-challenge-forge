import os
import shutil
import uuid
from pathlib import Path

SCRIPT_PATH = Path(os.path.dirname(os.path.realpath(__file__)))
RESOURCES_PATH = SCRIPT_PATH / "resources"


def enrich_phase_context(context):
    """Enriches the "phase" value of the context to simplify templating"""
    phase_context = context["phase"]

    for ci in [
        *phase_context["inputs"],
        *phase_context["outputs"],
    ]:
        ci["is_json"] = ci["kind"] == "Anything" or ci[
            "relative_path"
        ].endswith(".json")
        ci["is_image"] = ci["super_kind"] == "Image"

    phase_context["has_input_json"] = any(
        ci["is_json"] for ci in phase_context["inputs"]
    )

    phase_context["has_output_json"] = any(
        ci["is_json"] for ci in phase_context["outputs"]
    )

    phase_context["has_input_image"] = any(
        ci["is_image"] for ci in phase_context["inputs"]
    )

    phase_context["has_output_image"] = any(
        ci["is_image"] for ci in phase_context["outputs"]
    )


def create_civ_stub_file(*, target_dir, component_interface):
    """Creates a stub based on a component interface"""
    target_dir.parent.mkdir(parents=True, exist_ok=True)
    if component_interface["is_json"]:
        src = RESOURCES_PATH / "example.json"
    elif component_interface["is_image"]:
        target_dir = target_dir / f"{str(uuid.uuid4())}.mha"
        target_dir.parent.mkdir(parents=True, exist_ok=True)
        src = RESOURCES_PATH / "example.mha"
    else:
        target_dir.parent.mkdir(parents=True, exist_ok=True)
        src = RESOURCES_PATH / "example.txt"

    shutil.copy(src, target_dir)


def ci_to_civ(component_interface):
    """Creates a stub dict repr of a component interface value"""
    civ = {
        "file": None,
        "image": None,
        "value": None,
    }
    if component_interface["super_kind"] == "Image":
        civ["image"] = {
            "name": "the_original_filename_of_the_file_that_was_uploaded.suffix",
        }
    if component_interface["super_kind"] == "File":
        civ["file"] = (
            f"https://grand-challenge.org/media/some-link/"
            f"{component_interface['relative_path']}"
        )
    if component_interface["super_kind"] == "Value":
        civ["value"] = '{"some_key": "some_value"}'
    return {
        **civ,
        "interface": component_interface,
    }
