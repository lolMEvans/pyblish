def get_available_linestyles():
    """Get linestyles accepted by matplotlib.lines.Line2D objects.
    Returns:
        Available linestyles.
    """
    return "solid: '-'\n" \
           "dashed: '--'\n" \
           "dashed-dotted: '-.'\n" \
           "dotted: ':'\n" \
           "custom sequence: '(offset, on-off-dash-sequence)'"


def get_available_scales(keywords):
    """Get axes scales accepted by matplotlib.axis.(X/Y)Axis) objects and their respective keyword arguments if
    requested.
        For this implementation the axes names at the end of keywords (e.g. 'basex' etc.) are not required as the
        axis name is added automatically when setting axes scales.
    Args:
        keywords (bool): Whether to return the descriptors or accepted keywords for each scale.
    Returns:
        Available axes scales and corresponding keywords.
    """
    if(keywords):
        return "linear: {}\n" \
               "log: {base: Logarithm base\n" \
               "      nonpos: Whether to \'mask\' or \'clip\' non positive values\n" \
               "      subs: Positions of minor ticks in integer spacings}\n" \
               "symlog: {base: Logarithm base\n" \
               "         linthresh: Linear range (-x, x) of plot to avoid errors near zero\n" \
               "         subs: Positions of minor ticks in integer spacings\n" \
               "         linscale: Stretching of linear range \'linthresh\' relative to log range\n" \
               "logit: {nonpos: Whether to \'mask\' or \'clip\' values near 0 or 1}"
    else:
        return "linear: Linear scale\n" \
                "log: Logarithmic scale\n" \
                "symlog: Symmetrical log scale in both +ve and -ve directions\n" \
                "logit: Log scale near 0 and 1 - maps [0, 1] onto [-infinity, + infinity]"


def get_available_legend_locs():
    return "0: best\n" \
           "1: upper right\n" \
           "2: upper left\n" \
           "3: lower_right\n" \
           "4: lower_left\n" \
           "5: right\n" \
           "6: center left\n" \
           "7: center right\n" \
           "8: lower center\n" \
           "9: upper center\n" \
           "10: center"
