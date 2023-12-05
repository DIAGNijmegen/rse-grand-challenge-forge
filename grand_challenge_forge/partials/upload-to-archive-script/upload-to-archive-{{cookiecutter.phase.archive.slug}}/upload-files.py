"""
This script shows an example how to use GC-API to programmatically upload
files to an archive.

Remember, an archive is used to pull data per phase for a challenge. Each
phase has a designated archive. The archive is approached using its slug.

For your challenge, and this phase it is '{{cookiecutter.phase.archive.slug}}'.

Before you can run this script, you need to:
 * install gc-api (`pip install gcapi`)
 * update the EXPECTED_FILES
 * update the API_TOKEN with a personal token

Get a token from Grand Challenge:
  https://grand-challenge.org/settings/api-tokens/create/

For additional information about using gc-api and tokens, visit:
  https://grand-challenge.org/documentation/what-can-gc-api-be-used-for/#your-personal-api-token

Note that Grand-Challenge does its own post-processing on the files and the archive
will be filled with the result of this post-processing.

Check your uploaded results here:
 {{cookiecutter.phase.archive.url}}

Happy uploading!
"""

from pathlib import Path

import gcapi

API_TOKEN = "REPLACE-ME-WITH-YOUR-TOKEN"

ARCHIVE_SLUG = "{{cookiecutter.phase.archive.slug}}"

EXPECTED_CASES = [
    # for interfaces: {%+ for ci in cookiecutter.phase.inputs -%}{{ci.slug}}{%- if not loop.last -%}, {% endif -%}{%+ endfor %}
{%- for expected_cases in cookiecutter.phase.expected_cases %}
    {{ expected_cases }},
{%- endfor +%}
]


def main():
    check_files()
    upload_files()
    return 0


def check_files():
    # Perform a sanity-check to see if we have all the files we expect
    for case in EXPECTED_CASES:
        for file in case:
            path = Path(file)
            if not path.exists():
                raise RuntimeError(
                    f"Could not find {path.absolute()}, check that you're running in the right directory"
                )


def upload_files():
    # Uploads files to the Grand-Challenge archive

    client = gcapi.Client(token=API_TOKEN)
    archive = client.archives.detail(slug=ARCHIVE_SLUG)
    archive_api_url = archive["api_url"]

    for case in EXPECTED_CASES:
        print(f"Uploading {case} to {archive['title']}")

        content = map_case_files_to_interface(*case)
        archive_item = client.archive_items.create(archive=archive_api_url, values=[])
        client.update_archive_item(
            archive_item_pk=archive_item["pk"],
            values=content,
        )


def map_case_files_to_interface(case):
    return {
        {%- for ci in cookiecutter.phase.inputs %}
        "{{ci.slug}}": [Path(case[{{loop.index}}])],
        {%- endfor +%}
    }

if __name__ == "__main__":
    raise SystemExit(main())
