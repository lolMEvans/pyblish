import re


def parse_str_ranges(str_in):
    """Generate a flattened range of numbers given an input of colon-dash-and-comma-separated numbers.
    Args:
        str_in (str): Range of numbers requested.
            colon separated = range between
                e.g. 0:2 = 0, 1, 2
            comma separated = individual number
                e.g. 5, 6, 7 = 5, 6, 7
    Returns:
        (list): Parsed number ranges.
    """
    def range_unpacker(match):
        return "{}".format(','.join([str(_) for _ in range(int(match.group(1)), int(match.group(2))+1)]))
    # Convert colon-separated values into integer ranges and then convert to comma-separated string list
    range_unpacked = re.sub('([+-]?\d+):([+-]?\d+)', range_unpacker, str_in)

    if(len(range_unpacked) > 0):
        return [int(_) for _ in range_unpacked.split(',')]  # Convert comma-separated string list into integer list
    else:
        raise ValueError("Input string '{}' can not be parsed into integer ranges.".format(str_in))