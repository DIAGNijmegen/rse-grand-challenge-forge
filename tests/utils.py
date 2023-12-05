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


def pack_context_factory(**kwargs):
    result = deepcopy(DEFAULT_PACK_CONTEXT_STUB)
    for k, v in kwargs.items():
        result["challenge"][k] = v
    return result
