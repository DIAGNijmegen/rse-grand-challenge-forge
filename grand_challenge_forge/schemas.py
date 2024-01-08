import logging

import jsonschema

from grand_challenge_forge.exceptions import InvalidContextError
from grand_challenge_forge.utils import truncate_with_epsilons

logger = logging.getLogger(__name__)

ARCHIVE_SCHEMA = {
    "type": "object",
    "properties": {
        "slug": {"type": "string"},
        "url": {"type": "string"},
    },
    "required": ["slug", "url"],
}

COMPONENT_INTERFACE_SCHEMA = {
    "type": "object",
    "properties": {
        "slug": {"type": "string"},
        "relative_path": {"type": "string"},
        "kind": {"type": "string"},
        "super_kind": {"type": "string"},
    },
    "required": [
        "slug",
        "relative_path",
        "kind",
        "super_kind",
    ],
}


PACK_CONTEXT_SCHEMA = {
    "type": "object",
    "properties": {
        "challenge": {
            "type": "object",
            "properties": {
                "slug": {"type": "string"},
                "archives": {"type": "array", "items": ARCHIVE_SCHEMA},
                "phases": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "slug": {"type": "string"},
                            "archive": ARCHIVE_SCHEMA,
                            "algorithm_inputs": {
                                "type": "array",
                                "items": COMPONENT_INTERFACE_SCHEMA,
                            },
                            "algorithm_outputs": {
                                "type": "array",
                                "items": COMPONENT_INTERFACE_SCHEMA,
                            },
                        },
                        "required": [
                            "slug",
                            "archive",
                            "algorithm_inputs",
                            "algorithm_outputs",
                        ],
                        "additionalProperties": True,  # Allow additional properties
                    },
                },
            },
            "required": ["slug", "phases", "archives"],
        },
    },
    "required": ["challenge"],
    "additionalProperties": True,  # Allow additional properties
}


def validate_pack_context(context):
    try:
        jsonschema.validate(instance=context, schema=PACK_CONTEXT_SCHEMA)
        logging.debug("Context valid")
    except jsonschema.exceptions.ValidationError as e:
        raise InvalidContextError(
            f"Invalid pack context provided:\n'{truncate_with_epsilons(context)!r}'"
        ) from e
