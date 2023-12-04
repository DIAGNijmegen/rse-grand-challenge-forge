import logging

from challenge_forge.schemas import validate_pack_context

logger = logging.getLogger(__name__)


def generate_challenge_pack(*, context, output_directory):
    validate_pack_context(context)
