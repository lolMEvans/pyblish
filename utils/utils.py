import collections
import re


def conditional_decorator(condition, decorator, decorator_args, module):
    """Wrap a function in a decorator if a condition is True-
    avoiding trying to import the function until condition is met for e.g. a function only exists for python version 3.
    Args:
        condition (bool): Whether to wrap the function in a decorator.
        decorator (str): String name of decorator to use.
        decorator_args: Argument(s) to be passed to decorator.
        module: Module that decorator function resides in so that this function
            can call the decorator function without importing.
    Return:
        Either the original function or a decorated original function depending on condition.
    """
    if(condition):
        decorator = getattr(module, decorator) if module else eval(decorator)
        return decorator(decorator_args)
    else:
        return lambda x: x


def get_iterable(arg):
    """Convert any object into an iterable- objects that are already iterables are returned as is
    whereas non-iterable objects are converted to a list.
    Args:
        arg: Input argument to convert to iterable.
    Returns:
        Object as an iterable.
    """
    if isinstance(arg, collections.Iterable) and not isinstance(arg, str):
        return arg
    else:
        return [arg]


def map_list(list_in, map_len):
    """Map one list onto another with truncation or sequence repeating if necessary
    Args:
        list_in (list): Array to map.
        map_len (int): Length to map list to.
    Returns:
        (list): Array mapped to correct length.
    """
    try:
        return list_in * (map_len // len(list_in)) + list_in[:map_len % len(list_in)]
    except ValueError:
        raise ValueError("Could not map list {} to length {}".format(list_in, map_len))


def remove_empty_keys(dict_in):
    """Remove keys with any value entries that are None
    Args:
        dict_in (dict): Dictionary to remove non-value keys from.
    """
    return {k: v for k, v in dict_in.items() if all(vi is not None for vi in get_iterable(v))}


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
