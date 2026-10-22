"""Build labels for a small report."""


def report_labels(values):
    result = []
    for value in values:
        if value is not None:
            if value.strip():
                label = value.strip().lower().replace(" ", "-")
                result.append(label)
    return result
