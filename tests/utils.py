from copy import deepcopy

# Do not format, that way it can be used as copy and paste example in CLI

# fmt: off
DEFAULT_PACK_CONTEXT_STUB = {
    "challenge": {
        "slug": "challenge-slug",
        "phases": [
            {
                "slug": "phase-slug",
                "archive": {
                    "url": "https://grand-challenge.org/archives/archive-slug/"
                },
                "inputs": [
                    {
                        "slug": "input-ci-slug",
                        "kind": "Segmentation",
                        "super_kind": "Image",
                        "relative_path": "images/input-value"
                    },
                    {
                        "slug": "another-input-ci-slug",
                        "kind": "Anything",
                        "super_kind": "File",
                        "relative_path": "another-input-value.json"
                    }
                ],
                "outputs": [
                    {
                        "slug": "output-civ-slug",
                        "kind": "Image",
                        "super_kind": "Image",
                        "relative_path": "images/output-value"
                    },
                    {
                        "slug": "another-output-civ-slug",
                        "kind": "Anything",
                        "super_kind": "File",
                        "relative_path": "output-value.json"
                    }
                ]
            },
            {
                "slug": "another-phase-slug",
                "archive": {
                    "url": "https://grand-challenge.org/archives/another-archive-slug/"
                },
                "inputs": [
                    {
                        "slug": "input-ci-slug",
                        "kind": "Image",
                        "super_kind": "Image",
                        "relative_path": "images/input-value"
                    }
                ],
                "outputs": [
                    {
                        "slug": "another-output-civ-slug",
                        "kind": "Anything",
                        "super_kind": "File",
                        "relative_path": "output-value.json"
                    }
                ]
            }
        ]
    }
}
# fmt: on

counter = 0


def pack_context_factory(should_fail=False, **kwargs):
    global counter
    result = deepcopy(DEFAULT_PACK_CONTEXT_STUB)
    for k, v in kwargs.items():
        result["challenge"][k] = v

    def recursive_set_fail(d):
        if isinstance(d, dict):
            d["__should_fail"] = True  # Any value will do
            for item in d.values():
                recursive_set_fail(item)
        elif isinstance(d, list):
            for item in d:
                recursive_set_fail(item)

    if should_fail:
        recursive_set_fail(result)

    # Ensure unique slugs
    result["challenge"]["slug"] = result["challenge"]["slug"] + f"-{counter}"

    for phase in result["challenge"]["phases"]:
        phase["slug"] = phase["slug"] + f"-{counter}"

    counter = counter + 1
    return result
