import os
import re
import shutil
import uuid
from pathlib import Path

SCRIPT_PATH = Path(os.path.dirname(os.path.realpath(__file__)))
RESOURCES_PATH = SCRIPT_PATH / "resources"


def is_json(component_interface):
    return component_interface["relative_path"].endswith(".json")


def is_image(component_interface):
    return component_interface["super_kind"] == "Image"


def is_file(component_interface):
    return component_interface[
        "super_kind"
    ] == "File" and not component_interface["relative_path"].endswith(".json")


def extract_slug(url):
    # Define a regex pattern to match the slug in the URL
    pattern = r"/([^/]+)/*$"

    # Use re.search to find the match
    match = re.search(pattern, url)

    # If a match is found, extract and return the slug
    if match:
        slug = match.group(1)
        return slug
    else:
        # Return None or handle the case where no match is found
        return None


def create_civ_stub_file(*, target_dir, component_interface):
    """Creates a stub based on a component interface"""
    target_dir.parent.mkdir(parents=True, exist_ok=True)
    if is_json(component_interface):
        src = RESOURCES_PATH / "example.json"
    elif is_image(component_interface):
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
