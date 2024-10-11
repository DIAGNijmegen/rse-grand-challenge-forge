import pytest
from jinja2.exceptions import SecurityError

from grand_challenge_forge.generation_utils import get_jinja2_environment


def test_jinja2_environment_sandbox():
    # Get the Jinja2 environment
    env = get_jinja2_environment()

    # Sanity
    template = env.from_string("Hello, {{ name }}!")
    assert template.render(name="World") == "Hello, World!"

    template = env.from_string("{{ [].__class__.__mro__ }}")
    with pytest.raises(SecurityError):
        template.render()
