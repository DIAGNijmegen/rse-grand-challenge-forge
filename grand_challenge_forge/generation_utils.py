import json
import os
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

import black
from jinja2 import FileSystemLoader, StrictUndefined, TemplateNotFound
from jinja2.sandbox import ImmutableSandboxedEnvironment

from grand_challenge_forge import PARTIALS_PATH
from tests.utils import DEBUG

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


def has_example_value(component_interface):
    return (
        "example_value" in component_interface
        and component_interface["example_value"] is not None
    )


def create_civ_stub_file(*, target_path, component_interface):
    """Creates a stub based on a component interface"""
    target_path.parent.mkdir(parents=True, exist_ok=True)

    if has_example_value(component_interface):
        target_path.write_text(
            json.dumps(
                component_interface["example_value"],
                indent=4,
            )
        )
        return

    # Copy over an example
    if is_json(component_interface):
        shutil.copy(RESOURCES_PATH / "example.json", target_path)
    elif is_image(component_interface):
        target_path = target_path / f"{str(uuid.uuid4())}.mha"
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(RESOURCES_PATH / "example.mha", target_path)
    else:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(RESOURCES_PATH / "example.txt", target_path)


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
        civ["value"] = component_interface.get(
            "example_value", {"some_key": "some_value"}
        )
    return {
        **civ,
        "interface": component_interface,
    }


def get_jinja2_environment(searchpath=None):
    from grand_challenge_forge.partials.filters import custom_filters

    if searchpath:
        searchpath = [searchpath, PARTIALS_PATH]
    else:
        searchpath = PARTIALS_PATH

    env = ImmutableSandboxedEnvironment(
        loader=FileSystemLoader(
            searchpath=searchpath,
            followlinks=True,
        ),
        undefined=StrictUndefined,
    )
    env.filters = custom_filters
    env.globals["now"] = datetime.now(timezone.utc)

    return env


def copy_and_render(
    *,
    templates_dir_name,
    output_path,
    context,
):
    source_path = PARTIALS_PATH / templates_dir_name

    if not source_path.exists():
        raise TemplateNotFound(source_path)

    # Create the output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)

    env = get_jinja2_environment(searchpath=source_path)

    for root, _, files in os.walk(source_path, followlinks=True):
        root = Path(root)

        check_allowed_source(path=root)

        # Create relative path
        rel_path = root.relative_to(source_path)
        current_output_dir = output_path / rel_path

        # Create directories in the output path
        current_output_dir.mkdir(parents=True, exist_ok=True)

        for file in sorted(files):
            source_file = root / file
            output_file = current_output_dir / file

            check_allowed_source(path=source_file)

            if file.endswith(".j2"):
                # Render Jinja2 template
                template = env.get_template(
                    name=str(source_file.relative_to(source_path))
                )
                rendered_content = template.render(
                    **context,
                    _no_gpus=DEBUG,
                )

                # Write rendered content to output file (without .j2 extension)
                output_file = output_file.with_suffix("")
                with output_file.open("w") as f:
                    f.write(rendered_content)

                # Copy permission bits
                shutil.copymode(source_file, output_file)
            else:
                # Copy non-template files
                shutil.copy2(source_file, output_file)

    apply_black(output_path)


def check_allowed_source(path):
    if PARTIALS_PATH.resolve() not in path.resolve().parents:
        raise PermissionError(
            f"Only files under {PARTIALS_PATH} are allowed "
            "to be copied or rendered"
        )


def apply_black(target_path):
    for python_file in target_path.glob("**/*.py"):
        # Use direct black format call because black
        # CLI entrypoint ignores files in .gitignore

        black.format_file_in_place(
            python_file,
            fast=False,
            mode=black.Mode(),
            write_back=black.WriteBack.YES,
        )
