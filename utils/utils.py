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
    return array * (map_len // len(array)) + array[:map_len % len(array)]


def remove_empty_keys(dict):
    # Remove keys with any value entries that are None
    return {k: v for k,v in dict.items() if all(vi is not None for vi in get_iterable(v))}


def parse_str_ranges(str_in):
    '''Generate a flattened range of numbers given an input of colon-dash-and-comma-separated numbers.
    Args:
        str_in (str): Range of numbers requested.
            colon/dash separated = range between
                e.g. 0:2 = 0, 1, 2
                e.g. 1-4 = 1, 2, 3, 4
            comma separated = individual number
                e.g. 5, 6, 7 = 5, 6, 7

    Returns:
        (list): Flattened list of all numbers within input ranges.
    '''
    range_colon = [list(range(r[0], r[1]+1)) for r in [[int(x) for x in c.split(':')] for c in re.findall('\d+:\d+', str_in)]]
    range_dash = [list(range(r[0], r[1]+1)) for r in [[int(x) for x in c.split('-')] for c in re.findall('\d+-\d+', str_in)]]
    range_comma = [[int(x) for x in c.split(',')] for c in re.findall('\d+,\d+', str_in)]
    # Flatten, numerically sort and remove duplicates from resultant lists
    if(len(range_colon) > 0 or len(range_dash) > 0 or len(range_comma) > 0):
        return list(set(sorted([item for sublist in range_colon + range_dash + range_comma for item in sublist])))
    else:
        if(str_in.isdigit()):
            return [int(str_in)]
        else:
            raise ValueError("input string '{}' can not be parsed into integer ranges.".format(str_in))

def exp_to_log(x, p):
    return "{:.0f}".format(math.log10(x))

