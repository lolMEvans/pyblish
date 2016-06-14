from matplotlib.colors import LinearSegmentedColormap, ColorConverter


class ColorsError(Exception):
    pass


class PositionsError(Exception):
    pass


class InputError(Exception):
    pass


def make_colormap(colors, positions=None, reverse=False):
    """
    Returns a color map generated from an input list of colors and positions.

    Args:
        colors (list): A list of at least two colors - e.g. ['red', 'orange'].
            The colors can be a RGB(A) tuple, hex string or recognised name.
            An alpha value can be also be given for each color in a list - e.g. [['red', 0.5], ['#ff9900', 0.1]]

        positions (Optional[list]): The positions must be in a range from 0.0 to 1.0 that denotes the color map start and end.
            If no positions are set the colors are spaced equally.
        reverse (Optional[bool]): Reverse colors (list) if True. Defaults to False.

    Returns:
        LinearSegmentedColormap: A linear gradient created from the input positions and colors.

    Raises:
        ColorsError: The input colors list is of the wrong form.
        PositionsError: The input positions list is of the wrong form.
    """

    if(type(colors) is not list or (type(colors) is list and len(colors) < 2)):
        raise ColorsError("Colors must be a list that contains at least two values.")
    if(positions is not None):
        if(type(positions) is not list or (type(positions) is list and len(positions) < 2)):
            raise PositionsError("Positions must be None or a list that contain at least two values.")
        elif not(len(colors) == len(positions)):
            raise InputError("The same number of positions and colors must be defined unless positions is None.")

        # Check positions are within allowed range
        if(any([(p < 0.0 or p > 1.0) for p in positions])):
            raise PositionsError("Positions must all be within the range 0.0 - 1.0")

        if not(sorted(positions) == positions):
            raise PositionsError("Positions must be in ascending order.")

        # Pad out positions and color arrays if positions does not start or end in 0.0 or 1.0, respectively.
        if not(positions[0] == 0):
            positions.insert(0, 0.)
            colors.insert(0, colors[0])
        if not(positions[-1] == 1.0):
            positions.append(1.0)
            colors.append(colors[-1])
    else:
        # Auto generate list of positions if not specified
        positions = [p/float(len(colors)-1) for p in range(len(colors))]

    if(reverse):
        colors = colors[::-1]

    cc = ColorConverter()
    color_dict = {'red': [], 'blue': [], 'green':[], 'alpha':[]}
    for color, pos in zip(colors, positions):
        if(type(color) is list):
            color_val = color[0]
            color_alpha = color[1]
        elif(type(color) is tuple):
            color_val = list(color)
            color_alpha = 1.0 if len(color_val) < 4 else None
        elif(type(color) is str):
            color_val = color
            color_alpha = 1.0
        else:
            raise ColorsError("Unrecognised color type. Colors must be a list, tuple or string.")

        if(type(color_val) is str):
            rgba = cc.to_rgba(color_val, color_alpha)
        else:
            rgba = color_val if color_alpha is None else color_val + [color_alpha]

        # Add RGBA values to color dictionary
        color_dict['red'].append([pos, rgba[0], rgba[0]])
        color_dict['green'].append([pos, rgba[1], rgba[1]])
        color_dict['blue'].append([pos, rgba[2], rgba[2]])
        color_dict['alpha'].append([pos, rgba[3], rgba[3]])

    # Return linearly interpolated colormap if dictionary is not missing values
    if(all([color_dict[col] == 0 for col in ['red', 'green', 'blue', 'alpha']])):
        raise InputError("Colors and positions must be lists that contain at least two values.")
    else:
        return LinearSegmentedColormap('colormap', color_dict)


def show_colormap(colormap):
    import matplotlib.pyplot as plt
    import numpy as np

    x = np.linspace(0, 1, 100)
    xm, ym = np.meshgrid(x, x)
    numlevs = np.linspace(xm.min(), xm.max(), 100)
    plt.contourf(xm, c=xm, levels=numlevs, cmap=colormap)
    plt.colorbar()
    plt.show()
