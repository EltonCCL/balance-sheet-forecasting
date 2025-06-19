def sum_dict_values(d):
    """
    Recursively sums the values in a nested dictionary.
    """
    total = 0
    for key, value in d.items():
        if isinstance(value, dict):
            total += sum_dict_values(value)
        else:
            total += value
    return total


def build_recursively(sub_map, data_source):
    """Recursively build the dictionary."""
    result = {}
    for key, value in sub_map.items():
        if isinstance(value, dict):
            result[key] = build_recursively(value, data_source)
        else:
            result[key] = data_source.get(value)
    return result
