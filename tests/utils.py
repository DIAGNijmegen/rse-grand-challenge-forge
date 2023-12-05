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


def deep_merge_dicts(dict1, dict2):
    """Deep merge two dictionaries, including merging lists of dictionaries."""
    if not isinstance(dict1, dict) or not isinstance(dict2, dict):
        return dict2

    result = deepcopy(dict1)  # Create a copy of dict1

    for key, value2 in dict2.items():
        if key in result:
            value1 = result[key]
            if isinstance(value1, list) and isinstance(value2, list):
                # If both values are lists, merge them
                result[key] = [
                    deep_merge_dicts(v1, v2)
                    for v1, v2 in zip(value1, value2, strict=False)
                ]
                result[key] = result[key] + value2[len(value1) :]
            elif isinstance(value1, dict) and isinstance(value2, dict):
                # If both values are dictionaries, recursively merge them
                result[key] = deep_merge_dicts(value1, value2)
            else:
                # Otherwise, override the value in dict1 with the value in dict2
                result[key] = value2
        else:
            # If the key is not in dict1, add it to the result
            result[key] = value2

    return result
