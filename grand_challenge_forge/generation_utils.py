import os
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

from jinja2 import FileSystemLoader, StrictUndefined
from jinja2.sandbox import ImmutableSandboxedEnvironment

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


def create_civ_stub_file(*, target_path, component_interface):
    """Creates a stub based on a component interface"""
    target_path.parent.mkdir(parents=True, exist_ok=True)
    if is_json(component_interface):
        src = RESOURCES_PATH / "example.json"
    elif is_image(component_interface):
        target_path = target_path / f"{str(uuid.uuid4())}.mha"
        target_path.parent.mkdir(parents=True, exist_ok=True)
        src = RESOURCES_PATH / "example.mha"
    else:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        src = RESOURCES_PATH / "example.txt"

    shutil.copy(src, target_path)


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


def get_jinja2_environment(searchpath=None):
    from grand_challenge_forge.partials.filters import custom_filters

    env = ImmutableSandboxedEnvironment(
        loader=FileSystemLoader(searchpath=searchpath or []),
        undefined=StrictUndefined,
    )
    env.filters = custom_filters
    env.globals["now"] = datetime.now(timezone.utc)

    return env


def copy_and_render(
    *,
    source_path,
    output_path,
    context,
):
    # Create the output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)

    env = get_jinja2_environment(searchpath=source_path)

    for root, _, files in os.walk(source_path):
        root = Path(root)
        # Create relative path
        rel_path = root.relative_to(source_path)
        current_output_dir = output_path / rel_path

        # Create directories in the output path
        current_output_dir.mkdir(parents=True, exist_ok=True)

        for file in files:
            source_file = root / file
            output_file = current_output_dir / file

            if file.endswith(".j2"):
                # Render Jinja2 template
                template = env.get_template(
                    str(source_file.relative_to(source_path))
                )
                rendered_content = template.render(**context)

                # Write rendered content to output file (without .j2 extension)
                output_file = output_file.with_suffix("")
                with output_file.open("w") as f:
                    f.write(rendered_content)

                # Copy permission bits
                shutil.copymode(source_file, output_file)
            else:
                # Copy non-template files
                shutil.copy2(source_file, output_file)
