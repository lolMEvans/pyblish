import collections
import re
import math


def get_iterable(arg):
    '''
    Convert any object into an iterable- objects that are already iterables are returned as is
    whereas non-iterable objects are converted to a list
    :param arg: Input argument to convert to iterable
    :return: Object as an iterable
    '''
    if isinstance(arg, collections.Iterable) and not isinstance(arg, str):
        return arg
    else:
        return [arg]


def map_array(array, map_len):
    '''
    Map one array onto another with truncation or sequence repeating if necessary
    :param array: [list] Array to map
    :param map_len: [int] Length to map array to
    :return: None
    '''
    try:
        return array * (map_len // len(array)) + array[:map_len % len(array)]
    except ValueError:
        print(array, len(array), map_len)
        print(map_len % len(array))
        print(map_len // len(array))
        return None



def remove_empty_keys(dict):
    # Remove keys with any value entries that are None
    return {k: v for k,v in dict.items() if all(vi is not None for vi in get_iterable(v))}


def parse_str_ranges(str_in):
    '''Generate a flattened range of numbers given an input of colon-dash-and-comma-separated numbers.
    Args:
        str_in (str): Range of numbers requested.
            colon separated = range between
                e.g. 0:2 = 0, 1, 2
            comma separated = individual number
                e.g. 5, 6, 7 = 5, 6, 7
    Returns:
        (list): Parsed number ranges.
    '''
    def range_unpacker(match):
        return "{}".format(','.join([str(_) for _ in range(int(match.group(1)), int(match.group(2))+1)]))
    # Convert colon-separated values into integer ranges and then convert to comma-separated string list
    range_unpacked = re.sub('([+-]?\d+):([+-]?\d+)', range_unpacker, str_in)

    if(len(range_unpacked) > 0):
        return [int(_) for _ in range_unpacked.split(',')]  # Convert comma-separated string list into integer list
    else:
        raise ValueError("input string '{}' can not be parsed into integer ranges.".format(str_in))

def exp_to_log(x, p):
    return "{:.0f}".format(math.log10(x))

