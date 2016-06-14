import collections


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


def convert_rgba(color):
    if(isinstance(color, tuple) and 3 < len(color) <= 4):
        return [color]
    else:
        return color

