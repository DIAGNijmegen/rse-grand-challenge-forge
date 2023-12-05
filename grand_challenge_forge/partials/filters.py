from cookiecutter.utils import simple_filter

from grand_challenge_forge.utils import extract_slug as util_extract_slug


@simple_filter
def extract_slug(url):
    return util_extract_slug(url)
