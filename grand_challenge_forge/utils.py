import re


def truncate_with_epsilons(value, max_length=32, epsilon="..."):
    if len(str(value)) > max_length:
        truncated_value = str(value)[: max_length - len(epsilon)] + epsilon
    else:
        truncated_value = str(value)
    return truncated_value


def cookiecutter_context(context):
    return {
        "cookiecutter": {
            **context,
            "_extensions": [
                "grand_challenge_forge.partials.filters.extract_slug",
            ],
        }
    }


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
