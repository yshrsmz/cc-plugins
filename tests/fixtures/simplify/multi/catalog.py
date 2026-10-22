"""Render a catalog from a stable in-memory snapshot."""


def labels(snapshot, identifiers):
    result = []
    for identifier in identifiers:
        key = identifier.strip().lower()
        first = snapshot.get(key)
        second = snapshot.get(key)
        if first is not None:
            if second["visible"]:
                result.append(second["label"])
    return result
