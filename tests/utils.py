from copy import deepcopy

# Do not format, that way it can be used as copy and paste example in CLI

# fmt: off
PACK_CONTEXT_STUB = {
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
                        "slug": "input-civ-slug",
                        "relative_path": "images/input-value"
                    },
                    {
                        "slug": "another-input-civ-slug",
                        "relative_path": "images/another-input-value"
                    }
                ],
                "outputs": [
                    {
                        "slug": "output-civ-slug",
                        "relative_path": "images/output-value"
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
                        "relative_path": "images/input-value"
                    },
                    {
                        "slug": "another-input-ci-slug",
                        "relative_path": "images/another-input-value"
                    }
                ],
                "outputs": [
                    {
                        "slug": "output-ci-slug",
                        "relative_path": "images/output-value"
                    }
                ]
            }
        ]
    }
}
# fmt: on


def pack_context_factory(overwrites=None):
    overwrites = overwrites or {}
    return deep_merge(
        PACK_CONTEXT_STUB,
        overwrites,
    )


def deep_merge(dict1, dict2):
    """Recursively merge two dictionaries."""
    merged = deepcopy(dict1)

    for key, value in dict2.items():
        if (
            key in merged
            and isinstance(merged[key], dict)
            and isinstance(value, dict)
        ):
            # Recursively merge dictionaries
            merged[key] = deep_merge(merged[key], value)
        else:
            # Non-dictionary values or new keys
            merged[key] = value

    return merged
