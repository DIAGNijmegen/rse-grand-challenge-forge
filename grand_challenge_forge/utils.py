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
