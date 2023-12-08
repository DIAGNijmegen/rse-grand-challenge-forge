import logging

import jsonschema

from grand_challenge_forge.exceptions import InvalidContextError
from grand_challenge_forge.utils import truncate_with_epsilons

logger = logging.getLogger(__name__)


PACK_CONTEXT_SCHEMA = {
    "type": "object",
    "properties": {
        "challenge": {
            "type": "object",
            "properties": {
                "slug": {"type": "string"},
                "phases": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "slug": {"type": "string"},
                            "archive": {
                                "type": "object",
                                "properties": {"url": {"type": "string"}},
                                "required": ["url"],
                            },
                            "inputs": {
                                "type": "array",
                                "items": {
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
                                },
                            },
                            "outputs": {
                                "type": "array",
                                "items": {
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
                                },
                            },
                        },
                        "required": ["slug", "archive", "inputs", "outputs"],
                        "additionalProperties": True,  # Allow additional properties
                    },
                },
            },
            "required": ["slug", "phases"],
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
