import re

from cookiecutter.utils import simple_filter


@simple_filter
def extract_slug(url):
    # Define a regex pattern to match the slug in the URL
    pattern = r"/([^/]+)/*$"

    # Use re.search to find the match
    match = re.search(pattern, url)

    # If a match is found, extract and return the slug
    if match:
        slug = match.group(1)
        return slug
    else:
        # Return None or handle the case where no match is found
        return None
