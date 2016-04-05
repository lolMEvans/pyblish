#!/usr/bin/python

#from __future__ import print_function

import warnings
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.ticker import FuncFormatter
import json
import re

from utils import utils

# ToDo: Main
# ***
# Confirm getter functions work correctly
# Getter functions return dictionary of key names as object names so that
# user can parse output as desired
# But output should be easily convertable into input that works in setter
# functions

# Spines = DONE!, Ticks = DONE!, Labels = DONE!, Lines = DONE!
# Markers = ?
# Texts = ?
# Legend = ?
# ***

# Finish function docstrings - nearly all done
# Add fuzzy logic to font name search?
# add custom exceptions to get functions?
# add custom exceptions to set functions?
# add exceptions to utils
# add memoization for caching of default parameters?

# set custom colour cycle for lines to nice sequence - integrate ColorMapper module as utils package


class DotDict(dict):
    """Dictionary object with dot notation access."""
    def __getattr__(self, attr):
        if(attr not in self):
            raise KeyError("'{}' is not an attribute of {}".format(attr, type(self).__name__))
        return self.get(attr)
    __setattr__= dict.__setitem__
    __delattr__= dict.__delitem__


def pyblishify(fig, num_cols, aspect='square', which_labels='all', which_ticks='all',
                   which_spines=('left', 'bottom'),
                   which_lines='all', which_markers='all', which_texts='all',
                   which_legend_lines='all', which_legend_markers='all', which_legend_texts='all',
                   change_log_scales=True):

    # Convert dictionary to DotDict- a dict wrapper that allows dot notation
    defaults_dict = DotDict(_load_defaults())
    # Set defaults that are dependent on number of columns requested
    defaults_dict = _set_params_defaults(defaults_dict, num_cols)
    # Override a selection of default rcParams
    _set_rcparams_defaults(defaults_dict)
    # Set mathtext font
    set_font(defaults_dict.default_mathtext, mathtext=True)

    # Convert aspect variable to number
    aspect_val = _get_aspect_val(aspect)
    # Set figure size
    fig_width, fig_height = _get_figure_size(num_cols, aspect_val)
    set_figure_size(fig, fig_width, fig_height, 2.0)

    # Apply changes to all axis objects in figure
    for ax in fig.axes:
        # Set axes spine properties using default spine properties
        if(which_spines):
            set_spine_props(ax, ['right', 'left'], spine_props=dict(
                    linewidth=defaults_dict.spine_width * 2, edgecolor=[(0.0, 0.0, 1.0, 1.0), 'red']),
                            hide_other_spines=True, duplicate_ticks=True)
        # Set axes label properties using default label properties
        if(which_labels):
            set_label_props(ax, 'all', label_props=dict(
                    fontsize=[defaults_dict.label_size*3, 20], fontname=['Arial', 'Comic Sans MS'], color=None))
        # Set axes ticks and ticklabel properties using default tick and ticklabel properties
        if(which_ticks):
            set_tick_props(ax, 'all', tick_props=dict(
                    size=defaults_dict.majortick_size*2, width=defaults_dict.line_width*2, color='green',
                    direction=defaults_dict.tick_dir, pad=defaults_dict.ticklabel_pad,
                    labelsize=defaults_dict.ticklabel_size, labelcolor='purple'),
                    tick_type='major')
            set_tick_props(ax, 'all', tick_props=dict(
                    size=defaults_dict.minortick_size, width=defaults_dict.line_width, color='blue',
                    direction=defaults_dict.tick_dir, pad=defaults_dict.ticklabel_pad,
                    labelsize=defaults_dict.ticklabel_size, labelcolor='red'),
                    tick_type='minor')
        # Set line properties using default line properties
        if(which_lines):
            if(ax.lines):
                set_line_props(ax, [0,1], line_props=dict(
                        linewidth=defaults_dict.line_width*2, linestyle='-',
                        color=defaults_dict.col_cycle))
        # Set marker properties using default marker properties
        if(which_markers):
            if(ax.collections):
                set_marker_props(ax, 'all', marker_props=dict(
                        sizes=[100, 400],#defaults_dict.marker_size,
                        linewidth=defaults_dict.line_width*2, linestyle=[['-', ':'], ['-', ':']],
                        facecolor=['red', 'green'], edgecolor=[defaults_dict.col_cycle]*2,
                        symbols=['x', 'x']))
        # Set text properties using default text properties
        if(which_texts):
            set_text_props(ax, 'all', text_props=dict(
                    fontsize=defaults_dict.texts_size, fontname='Arial',
                    color='green'))
        # Set legend properties using old legend properties and updated plotted lines and markers properties
        if(which_legend_lines or which_legend_markers or which_legend_texts):
            if(ax.get_legend() and (ax.lines or ax.collections)):
                set_legend_props(ax, 'all', None, '0:1',
                                 line_props=dict(linewidth=10),
                                 marker_props=dict(),
                                 text_props={'color': 'blue'})
        # Set axes log scale properties
        if(change_log_scales):
            set_log_exponents(ax, 'all')



# GETTER FUNCTIONS ----------------------------------------------------------------------------------------------------



def get_spine_props(ax, which_spines):
    """Get properties of spines.
    Args:
        ax (matplotlib.axes): Axis object.
        which_spines (int|str|matplotlib.spines.Spine): Spine index(es).
            Given as a specified type OR list of a specified type.
            Names accepted are 'left', 'bottom', 'right', 'top', or 'all' can be used to select all spines.
            Comma-dash-colon separated strings can be used to select axes in 'left', 'bottom', 'right', 'top' order.
                e.g. '0' = 'left', '0,1' = 'left, bottom', '1:3' = 'bottom, right, top'
    Returns:
        (dict): Spine properties for each spine specified (e.g. 'left', 'bottom', 'right', 'top') as a nested dictionary.
    """
    return _get_props(ax, which_spines, ax.spines, 'spine', ['left', 'bottom', 'right', 'top'])


def get_tick_props(ax, which_axes, tick_type='major'):
    """Get properties of ticks. Uses custom logic specifically for ticks as they are not gettable in the same way as
    other matplotlib objects.
    Args:
        ax (matplotlib.axes): Axis object.
        which_axes (int|str|matplotlib.axis.(XAxis|YAxis)): Axes index(es).
            Given as a specified type OR list of a specified type.
            Names accepted are 'x' or 'y', or 'all' can be used to select both axes.
            Comma-dash-colon separated strings can be used to select axes in 'x', 'y' order.
                e.g. '0' = 'x', '0,1' = 'x, y'
        tick_type (str): 'major' or 'minor'.
    Returns:
        (dict): Tick properties for each set of ticks specified (e.g. 'x', 'y') as a nested dictionary.
    """
    return _get_props(ax, which_axes, {'x': ax.xaxis, 'y': ax.yaxis}, 'tick', ['x', 'y'], tick_type)


def get_label_props(ax, which_axes):
    """Get properties of labels.
    Args:
        ax (matplotlib.axes): Axis object.
        which_axes (int|str|matplotlib.axis.(XAxis|YAxis)): Axes index(es).
            Given as a specified type OR list of a specified type.
            Names accepted are 'x' or 'y', or 'all' can be used to select both axes.
            Comma-dash-colon separated strings can be used to select axes in 'x', 'y' order.
                e.g. '0' = 'x', '0,1' = 'x, y'
    Returns:
        (dict): Label properties for each label specified (e.g. 'x', 'y') as a nested dictionary.
    """
    return _get_props(ax, which_axes, {'x': ax.xaxis.label, 'y': ax.yaxis.label}, 'label', ['x', 'y'])


def get_line_props(ax, which_lines, legend_lines=False):
    """Get properties of lines.
    Args:
        ax (matplotlib.axes): Axis object.
        which_lines (int|str|matplotlib.lines.Line2D): Line index(es).
            Given as a specified type OR list of a specified type.
            'all' can be used to select all lines.
            Comma-dash-colon separated strings can be used to select lines in plotted order.
                e.g. '0' = '1st line', '0,1' = '1st, 2nd line', '1:3' = '2nd, 3rd, 4th line'
        legend_lines (bool): Sets properties for legend lines if True, otherwise sets properties for lines plotted on
            specified axis object.
    Returns:
        (dict): Line properties for each line specified (e.g. '0', '1', 'all') as a nested dictionary.
    """
    if(legend_lines):
        # Get appropriate lines from legend handles
        lines_master = [h for h in ax.legend_.legendHandles if isinstance(h, matplotlib.lines.Line2D)]
        lines_name = 'legend line'
    else:
        lines_master = ax.lines
        lines_name = 'line'
    return _get_props(ax, which_lines, lines_master, lines_name)


def get_marker_props(ax, which_markers, legend_markers=False):
    """Get properties of marker collections.
    Args:
        ax (matplotlib.axes): Axis object.
        which_markers (int|str|matplotlib.collections.PathCollection): Marker collection/set index(es).
            Given as a specified type OR list of a specified type.
            'all' can be used to select all marker collections.
            Comma-dash-colon separated strings can be used to select marker collections in plotted order.
                e.g. '0' = '1st marker col', '0,1' = '1st, 2nd marker col', '1:3' = '2nd, 3rd, 4th marker col'
        legend_markers (bool): Sets properties for legend markers if True, otherwise sets properties for markers plotted
            on specified axis object.
    Returns:
        (dict): Marker properties for each marker collection specified (e.g. '0', '1', 'all') as a nested dictionary.
    """
    if(legend_markers):
        # Get appropriate markers from legend handles
        markers_master = [h for h in ax.legend_.legendHandles if isinstance(h, matplotlib.markers.marker2D)]
        markers_name = 'legend marker collection'
    else:
        markers_master = ax.collections
        markers_name = 'marker collection'
    return _get_props(ax, which_markers, markers_master, markers_name)


def get_text_props(ax, which_texts, legend_texts=False):
    """Get properties of texts.
    Args:
        ax (matplotlib.axes): Axis object.
        which_texts (int|str|matplotlib.texts.text2D): text index(es).
            Given as a specified type OR list of a specified type.
            'all' can be used to select all texts.
            Comma-dash-colon separated strings can be used to select texts in plotted order.
                e.g. '0' = '1st text', '0,1' = '1st, 2nd text', '1:3' = '2nd, 3rd, 4th text'
        legend_texts (bool): Sets properties for legend texts if True, otherwise sets properties for texts plotted on
            specified axis object.
    Returns:
        (dict): text properties for each text specified (e.g. '0', '1', 'all') as a nested dictionary.
    """
    if(legend_texts):
        # Get appropriate texts from legend handles
        texts_master = ax.legend_.texts
        texts_name = 'legend text'
    else:
        texts_master = ax.texts
        texts_name = 'text'
    return _get_props(ax, which_texts, texts_master, texts_name)


def get_legend_props(ax, which_lines=None, which_markers=None, which_texts=None):
    """Get properties of legend frame or lines or markers or texts. Frame properties are returned only if
    which_lines = which_markers = which_texts = None to avoid triply nested dictionaries as output.
    Args:
        ax (matplotlib.axes): Axis object.
        which_lines/which_markers/which_texts (int|str|matplotlib objects): Object index(es).
            Given as a specified type OR list of a specified type.
            'all' can be used to select all objects.
            Comma-dash-colon separated strings can be used to select objects in plotted order.
                e.g. '0' = '1st object', '0,1' = '1st, 2nd object', '1:3' = '2nd, 3rd, 4th object'
    Returns:
        (dict): text properties for each text specified (e.g. '0', '1', 'all') as a nested dictionary.
    """
    if(which_lines):
        return get_line_props(ax, which_lines, True)
    elif(which_markers):
        return get_marker_props(ax, which_markers, True)
    elif(which_texts):
        return get_text_props(ax, which_texts, True)
    else:
        # Get list of attributes to retrieve for legend using defaults.json file
        legend_attrs = list(DotDict(_load_defaults())['legend_props'].keys())
        legend_attrs_proper = legend_attrs.copy()  # Copy legend attributes
        # Fix copied attribute names from user-friendly defaults.json names to those that matplotlib uses internally
        legend_attrs_proper[legend_attrs_proper.index('loc')] = '_loc'
        legend_attrs_proper[legend_attrs_proper.index('ncol')] = '_ncol'
        legend_attrs_proper[legend_attrs_proper.index('frameon')] = '_drawFrame'
        # Create property dictionary using built in getter functions for matplotlib object and user-friendly attribute
        # names
        return {n: getattr(ax.legend_, k) for (k, n) in zip(legend_attrs_proper, legend_attrs)}


def get_props_from_nested_dict(nested, objs_name, objs_order):
    props = {}
    for i in objs_order:
        v = nested[i]
        for k, v in v.items():
            if(k in props):
                props[k].append(v)
            else:
                props[k] = [v]
    return props




# SETTER FUNCTIONS ----------------------------------------------------------------------------------------------------



def set_figure_size(fig, fig_width, fig_height, res_inc=1.0):
    """Set figure size by calling private function
    Args:
        fig (matplotlib.figure.Figure)
        fig_width (float)
        fig_height (float)
        res_inc (float): Factor to increase figure resolution by.
    Returns:
        None
    """
    _set_figure_size(fig, fig_width * res_inc, fig_height * res_inc)


def set_font(font, mathtext=False):
    """Set plot font (normal or mathtext). The method for setting mathtext is experimental and may be removed in future
    updates to matplotlib.
    Args:
        font: Font name.
        mathtext (bool): Sets mathtext rather than normal plot text if True.
    Returns:
        None
    """
    global_fontsets = ['cm', 'sans', 'stixsans']
    fonts = get_available_fonts()
    # Check if font is on system
    if(font in fonts + global_fontsets):
        if(mathtext):
            # Check if font is one of the 3 global fontsets
            if(font in global_fontsets):
                matplotlib.rcParams['mathtext.fontset'] = font
            else:
                matplotlib.rcParams['mathtext.fontset'] = 'custom'
                matplotlib.rcParams['mathtext.cal'] = font
                matplotlib.rcParams['mathtext.rm'] = font
                matplotlib.rcParams['mathtext.tt'] = font
                matplotlib.rcParams['mathtext.it'] = "{}:italic".format(font)
                matplotlib.rcParams['mathtext.bf'] = "{}:bold".format(font)
                matplotlib.rcParams['mathtext.sf'] = font
        else:
            matplotlib.rcParams['font.family'] = font
    else:
        warnings.warn("Could not set '{}' mathtext font so reverted back to default. "
                        "Use get_available_fonts() to see a list of fonts on this system.".format(font))


def set_spine_props(ax, which_spines, spine_props, hide_other_spines=True, duplicate_ticks=False):
    """Set properties of spines.
    Args:
        ax (matplotlib.axes): Axis object.
        which_spines (int|str|matplotlib.spines.Spine): Spine index(es).
            Given as a specified type OR list of a specified type.
            Names accepted are 'left', 'bottom', 'right', 'top', or 'all' can be used to select all spines.
            Comma-dash-colon separated strings can be used to select axes in 'left', 'bottom', 'right', 'top' order.
                e.g. '0' = 'left', '0,1' = 'left, bottom', '1:3' = 'bottom, right, top'
        spine_props (dict): Spine properties. Each property can be given as an appropriate type and will be applied to
            all spines. Alternatively, a list may be given for each property so that each spine is assigned different
            properties.
                linewidth (int): Spine width(s)
                edgecolor (str|tuple): Spine color(s) as hex string or RGB tuple
        hide_other_spines (bool): Hide unspecified spines if True.
        duplicate_ticks (bool): Duplicate ticks when both opposite sides of spines are visible if True.
    Returns:
        None
    """
    # Get appropriate spine object(s) from input as list
    which_spines = _get_plot_objects(which_spines, spine_props, ax.spines, 'spine',
                                     ['left', 'bottom', 'right', 'top'])
    print(which_spines)
    if(which_spines):
        spines = ax.spines
        spines_dict = {'left': ax.yaxis, 'bottom': ax.xaxis, 'right': ax.yaxis, 'top': ax.xaxis}
        # Get list of spines unspecified which will be made invisible
        which_spines_invis = [v for k,v in spines.items() if v not in which_spines]
        if(hide_other_spines):
            # Turn off all spines and ticks and tick labels
            for ax_dir in spines:
                spines[ax_dir].axis.set_tick_params(which='both', **{ax_dir: 'off'}, **{'label'+ax_dir: 'off'})
                spines[ax_dir].set_visible(False)
        # Show spines and ticks and tick labels for spines specified
        for sp in which_spines:
            ax_dir = list(spines.keys())[list(spines.values()).index(sp)]
            sp.axis.set_tick_params(which='both', **{ax_dir: 'on'}, **{'label'+ax_dir: 'on'})
            sp.set_visible(True)
            if not(duplicate_ticks):
                # Set ticks only on one side, according to which 'left'|'right', 'bottom'|'top' spine is ordered last
                # in which_spines
                sp.axis.set_ticks_position(ax_dir)
        # Handle RGB(A) color input
        if('color' in spine_props):
            if(isinstance(spine_props['color'], tuple) and 3 < len(spine_props['color']) <= 4):
                spine_props['color'] = [spine_props['color']]
        # Set properties using matplotlib.pyplot.setp
        _set_props(which_spines, 'spine', **spine_props)


def set_tick_props(ax, which_axes, tick_props, tick_type='major'):
    """Set properties for axes ticks. Uses custom logic specifically for ticks as they are not settable in the same
    way as other matplotlib objects.
    Args:
        ax (matplotlib.axes): Axis object.
        which_axes (int|str|matplotlib.axis.(XAxis|YAxis)) axes indexes.
            Given as a specified type OR list of a specified type.
            Names accepted are 'x' or 'y', or 'all' can be used to select both axes.
            Comma-dash-colon separated strings can be used to select axes in 'x', 'y' order.
                e.g. '0' = 'x', '0,1' = 'x, y'
        tick_props (dict): Tick properties. Each property can be given as an appropriate type and will be applied to
            all ticks. Alternatively, a list may be given for each property so that each tick collection is assigned
            different properties.
                size (int|float): Tick mark size(s)
                width (int|float): Tick mark width(s)
                color (str|tuple): Tick mark color(s) as hex string(s) or RGB tuple(s)
                direction (str): Tick mark direction: 'in' or 'out'
                pad (int|float): Padding between tick labels and tick marks
                labelsize (int|float): Tick label size(s)
                labelcolor (str|tuple): Tick label color(s) as hex string(s) or RGB tuple(s)
        tick_type (str): 'major' or 'minor'.
    Returns:
        None
    """
    if(tick_type not in ['major', 'minor']):
        print("ValueError: Tick type not recognised. Enter 'major' or 'minor'.")
    # Get appropriate axis/axes objects from input as list
    which_axes = _get_plot_objects(which_axes, tick_props, {'x': ax.xaxis, 'y': ax.yaxis}, tick_type + ' tick',
                                   ['x', 'y'])
    if(which_axes):
        # Set properties using ax.(x|y)axis.set_tick_params
        _set_props(which_axes, 'ticks', tick_type, **tick_props)


def set_label_props(ax, which_labels, label_props):
    """Set properties for axes labels.
    Args:
        ax (matplotlib.axes): Axis object.
        which_axes (int|str|matplotlib.axis.(XAxis|YAxis)) axes indexes.
            Given as a specified type OR list of a specified type.
            Names accepted are 'x' or 'y', or 'all' can be used to select both axes.
            Comma-dash-colon separated strings can be used to select axes in 'x', 'y' order.
                e.g. '0' = 'x', '0,1' = 'x, y'
        label_props (dict): Label properties. Each property can be given as an appropriate type and applied to all labels.
            Alternatively, a list may be given for each property so that each label is assigned different properties.
                fontsize (float): Label font size(s)
                fontname (str): Label font(s)
                color (str|tuple): Label color(s) as hex string(s) or RGB tuple(s)
    Returns:
        None
    """
    # Get appropriate axis label(s) objects from input as list
    which_labels = _get_plot_objects(which_labels, label_props, {'x': ax.xaxis.label, 'y': ax.yaxis.label}, 'label',
                                    ['x', 'y'])
    if(which_labels):
        # Check if there's mathtext if user requests a custom font as it will change font for
        # all mathtext in the plot
        # if('fontname' in label_props):
        #     _check_mathtext(ax, label_props['fontname'])
        # Set properties using matplotlib.pyplot.setp
        _set_props(which_labels, 'label', **label_props)


def set_line_props(ax, which_lines, line_props, legend_lines=False):
    """Set properties for lines.
    Args:
        ax (matplotlib.axes): Axis object.
        which_lines (int|str|matplotlib.lines.Line2D): Line index(es).
            Given as a specified type OR list of a specified type.
            'all' can be used to select all lines.
            Comma-dash-colon separated strings can be used to select lines in plotted order.
                e.g. '0' = '1st line', '0,1' = '1st, 2nd line', '1:3' = '2nd, 3rd, 4th line'
        line_props (dict): Line properties. Each property can be given as an appropriate type and applied to all lines.
            Alternatively, a list may be given for each property so that each line is assigned different properties.
                linewidth (int|float): Line width(s)
                color (str|tuple): Line color(s) as hex string(s) or RGB tuple(s)
                linestyle (str): Line style(s): '-', '--', ':'
        legend_lines (bool): Sets properties for legend lines if True, otherwise sets properties for lines plotted on
            specified axis object.
    Returns:
        None
    """
    if(legend_lines):
        lines_master = [h for h in ax.legend_.legendHandles if isinstance(h, matplotlib.lines.Line2D)]
        lines_name = 'legend line'
    else:
        lines_master = ax.lines
        lines_name = 'line'
    # Get appropriate line object(s) from input as list
    which_lines = _get_plot_objects(which_lines, line_props, lines_master, lines_name)
    if(which_lines):
        # Set properties using matplotlib.pyplot.setp
        _set_props(which_lines, lines_name, **line_props)


def set_marker_props(ax, which_markers, marker_props, legend_markers=False):
    """Set properties for markers.
    Args:
        ax (matplotlib.axes): Axis object.
        which_markers (int|str|matplotlib.collections.PathCollection): Marker collection/set index(es).
            Given as a specified type OR list of a specified type.
            'all' can be used to select all marker collections.
            Comma-dash-colon separated strings can be used to select marker collections in plotted order.
                e.g. '0' = '1st marker col', '0,1' = '1st, 2nd marker col', '1:3' = '2nd, 3rd, 4th marker col'
        marker_props (dict): Marker collection properties. Each property can be given as an appropriate type and
            applied to all marker collections. Alternatively, a list may be given for each property so that each marker
            collection is assigned different properties. Nested lists may also be given to change the properties of
            individual markers within collections.
                sizes (list): Marker size(s) applied to each marker within a collection
                linewidth (int|float): Marker line width(s)
                linestyle (str): Marker collection line style(s): '-', '--', ':'
                facecolor (str|tuple): Marker collection face color(s) as hex string(s) or RGB tuple(s)
                edgecolor (str|tuple): Marker collection line color(s) as hex string(s) or RGB tuple(s)
                symbols (str|matplotlib.markers.MarkerStyle): Marker symbols
        legend_markers (bool): Sets properties for legend marker collections if True, otherwise sets properties for
            marker collections plotted on specified axis object.
    Returns:
        None
    """
    if(legend_markers):
        markers_master = [h for h in ax.legend_.legendHandles if isinstance(h, matplotlib.collections.PathCollection)]
        markers_name = 'legend marker collection'
    else:
        markers_master = ax.collections
        markers_name = 'marker collection'
    # Get appropriate marker object(s) from input as list
    which_markers = _get_plot_objects(which_markers, marker_props, markers_master, markers_name)
    if(which_markers):
        # Convert any non-iterable size value to an iterable as this is the input for the built-in matplotlib function
        if('sizes' in marker_props):
            marker_props['sizes'] = [_ if isinstance(_, list) else [_] for _ in utils.get_iterable(marker_props['sizes'])]
        if('symbols' in marker_props):
            marker_props['paths'] = _get_marker_paths(utils.get_iterable(marker_props['symbols']))
            marker_props.pop('symbols')  # Remove symbols key as it is now paths
        # Set properties using matplotlib.pyplot.setp
        _set_props(which_markers, markers_name, **marker_props)


def set_text_props(ax, which_texts, text_props, legend_texts=False):
    """Set properties for texts.
    Args:
        ax (matplotlib.axes): Axis object.
        which_texts (int|str|matplotlib.text.Text): Text index(es).
            Given as a specified type OR list of a specified type.
            'all' can be used to select all texts.
            Comma-dash-colon separated strings can be used to select texts in plotted order.
                e.g. '0' = '1st text', '0,1' = '1st, 2nd text', '1:3' = '2nd, 3rd, 4th text'
        text_props (dict): Text properties. Each property can be given as an appropriate type and applied to all lines.
            Alternatively, a list may be given for each property so that each text is assigned different properties.
                fontsize (int|float): Text font size(s)
                color (str|tuple): Text font color(s) as hex string(s) or RGB tuple(s)
                fontname (str): Text font(s)
        legend_texts (bool): Sets properties for legend texts if True, otherwise sets properties for texts plotted on
            specified axis object.
    Returns:
        None
    """
    if(legend_texts):
        texts_master = ax.legend_.texts
        texts_name = 'legend text'
    else:
        texts_master = ax.texts
        texts_name = 'legend'
    # Get appropriate text object(s) from input as list
    which_texts = _get_plot_objects(which_texts, text_props, texts_master,
                                     texts_name)
    if(which_texts):
        # Set properties using matplotlib.pyplot.setp
        _set_props(which_texts, texts_name, **text_props)


def set_legend_props(ax, which_lines=None, which_markers=None, which_texts=None,
                        line_props=None, marker_props=None, text_props=None,
                        frame_props=None):
    """Set properties for legend frame and/or any lines, markers, texts. Changes to plotted lines and markers before
    this function call are reflected in the legend lines/symbols automatically.
    Args:
        ax (matplotlib.axes): Axis object.
        which_lines/which_markers/which_texts (int|str|matplotlib objects): Object index(es).
            Given as a specified type OR list of a specified type.
            'all' can be used to select all objects.
            Comma-dash-colon separated strings can be used to select objects in plotted order.
                e.g. '0' = '1st object', '0,1' = '1st, 2nd object', '1:3' = '2nd, 3rd, 4th object'
        line_props (dict): Line properties. Each property can be given as an appropriate type and applied to all lines.
            Alternatively, a list may be given for each property so that each line is assigned different properties.
                linewidth (int|float): Line width(s)
                color (str|tuple): Line color(s) as hex string(s) or RGB tuple(s)
                linestyle (str): Line style(s): '-', '--', ':'
        marker_props (dict): Marker collection properties. Each property can be given as an appropriate type and
            applied to all marker collections. Alternatively, a list may be given for each property so that each marker
            collection is assigned different properties. Nested lists may also be given to change the properties of
            individual markers within collections.
                sizes (list): Marker size(s) applied to each marker within a collection
                linewidth (int|float): Marker line width(s)
                linestyle (str): Marker collection line style(s): '-', '--', ':'
                facecolor (str|tuple): Marker collection face color(s) as hex string(s) or RGB tuple(s)
                edgecolor (str|tuple): Marker collection line color(s) as hex string(s) or RGB tuple(s)
                symbols (str|matplotlib.markers.MarkerStyle): Marker symbols
        text_props (dict): Text properties. Each property can be given as an appropriate type and applied to all lines.
            Alternatively, a list may be given for each property so that each text is assigned different properties.
                fontsize (int|float): Text font size(s)
                color (str|tuple): Text font color(s) as hex string(s) or RGB tuple(s)
                fontname (str): Text font(s)
        frame_props (dict): Legend frame properties. See matplotlib.legend documentation for full properties list.
            loc (int):
            ncol (int): Number of columns
            frameon (bool): Frame border is visible if True
            columnspacing (float): Spacing between columns
            labelspacing (float): Spacing between symbols and text labels
            handlelength (float): Length of handles (only applicable for lines)
            numpoints (int): Number of symbols (only applicable for markers used on a line plot)
            scatterpoints (int): Number of symbols (only applicable on a scatter plot)
            bbox_to_anchor (tuple|list): Coords to position legend: (x0, y0)
    Returns:
        None
    """

    # Assign legend properties - reverts to default values if not specified
    legend = ax.get_legend()
    # Get existing legend bbox coords and convert to axes coords
    bbox_axcoords = ax.transAxes.inverted().transform(legend.get_bbox_to_anchor().get_points())
    bbox_x0, bbox_y0 = bbox_axcoords[0][0], bbox_axcoords[0][1]
    # Position new legend in same place as old one if no frame properties defined or just no 'bbox'_to'anchor' is defined
    # Otherwise there would be no easy way of specifying that the new legend should be placed where the old one was
    if(frame_props is None):
        frame_props = {}  # Initialise frame properties dictionary
        frame_props['bbox_to_anchor'] = (bbox_x0, bbox_y0)
    else:
        frame_props['bbox_to_anchor'] = frame_props.get('bbox_to_anchor', (bbox_x0, bbox_y0))
    # Set frame properties regardless of whether the dictionary is given or individual properties are set
    # This is done because a new legend is plotted no matter what so need to send it at least coords
    for var_name in ['loc', 'ncol']:
        frame_props[var_name] = _get_frame_props(legend, frame_props, var_name, True)
    frame_props['frameon'] = _get_frame_props(legend, frame_props, 'drawFrame', True)
    for var_name in ['columnspacing', 'labelspacing', 'handlelength',
                     'numpoints', 'scatterpoints']:
        frame_props[var_name] = _get_frame_props(legend, frame_props, var_name)

    # Plot new legend with updated line and marker properties if they've been changed and specified legend properties
    ax.legend(**frame_props)

    # Set legend line properties
    set_line_props(ax, which_lines, line_props, legend_lines=True)
    # Set legend marker properties
    set_marker_props(ax, which_markers, marker_props, legend_markers=True)
    # Set legend text properties
    set_text_props(ax, which_texts, text_props, legend_texts=True)


def set_log_exponents(ax, which_axes):
    """
    Set tick labels as logarithmic exponents on requested x/y axis.
    Args:
        ax (matplotlib.axes): Axis object.
        which_axes (int|str|matplotlib.axis.(XAxis|YAxis)) axes indexes.
            Given as a specified type OR list of a specified type.
            Names accepted are 'x' or 'y', or 'all' can be used to select both axes.
    Returns:
        None
    """
    # Get appropriate axis/axes objects from input as list
    axes_dict = {'x': ax.xaxis, 'y': ax.yaxis}
    which_axes = _get_plot_objects(ax, which_axes, True, axes_dict,
                                    'Axes', (matplotlib.axis.XAxis, matplotlib.axis.YAxis),
                                    axes_dict.keys())
    if(which_axes):
        for wa in which_axes:
            # Check if axis scale is logarithmic or all tick labels are scientific notation
            # because in these cases we can assume exponential notation will be good
            if(wa.get_scale() == 'log' or all(['e' in str(t) for t in wa.get_majorticklocs()])):
                # Change exponentials notation to log notation - i.e. 10^2, 10^3 -> 2, 3
                wa.set_major_formatter(FuncFormatter(utils.exp_to_log))
                # Add log to label text if it's absent
                _append_log_text(wa)


# ToDo: Any other one-off functions for adjusting plotted features?


# PRIVATE GETTER FUNCTIONS --------------------------------------------------------------------------------------------

# Font related functions -----------------------------------------------
def get_available_fonts():
    """Use matplotlib.font_manager to get fonts on system.
    Returns:
         Alphabetically sorted list of .ttf font names.
    """
    FM = fm.FontManager()
    font_names = set([f.name for f in FM.ttflist])
    return sorted(font_names)


def _get_aspect_val(aspect):
    """Get width-to-height figure aspect ratio given name or value input.
    Args:
        aspect (str|float): Width-to-height figure aspect ratio name or value.
    Returns:
        aspect_return (float): Width-to-height figure aspect ratio.
    """
    aspect_dict = {'square': 1, 'normal': 1.333, 'golden': 1.618, 'widescreen': 1.78}
    # If aspect is a number use it directly
    # Otherwise look up aspect in a dictionary to convert to number
    if(isinstance(aspect, (float, int))):
        aspect_return = aspect
    elif(isinstance(aspect, str)):
        if(':' in aspect):
            numerator, denominator = aspect.split(':')
            aspect_return = float(numerator)/float(denominator)
        elif(aspect in aspect_dict):
            aspect_return = aspect_dict[aspect]
        else:
            print("InputError: unregonised apsect name. Accepted names are '{}'.".format("', '".join(aspect_dict.keys())))
            return None
    else:
        print("InputError: unrecognised aspect value. Accepted inputs are '{}' or a number.".format("', '".join(aspect_dict.keys())))
        return None
    return aspect_return


def _get_figure_size(num_cols, aspect):
    """Get size of figure based on number of columns that the figure will span.
    Args:
        num_cols: Number of columns specified.
        aspect (float): Width-to-height figure aspect ratio.
    Returns:
        (float), (float): Figure width, figure height.
    """
    fig_width = 3.333 if num_cols == 1 else 7.639  # One column or two columns + middle space
    fig_height = fig_width * 1./aspect
    return fig_width, fig_height


def _get_plot_objects(objs, objs_props, objs_master, objs_name, objs_keys=None):
    """Get plotted objects from parsed input.
    Args:
        objs (int|str|matplotlib objects): Object index(es).
            Input is converted to an iterable and parsed depending on type.
        objs_props: Properties to apply to element object(s). If None then objects were specified but no properties
            were, so an error is raised. For getter-like functions this is passed as False rather than None, even though
            no properties are specified, to avoid this error.
        objs_master (list|dict): If dict then it is converted to a list of values in order specified in objs_keys. The
            master list is used to retrieve correct object when given integer|str objs input.
        objs_name (str): Name of object to be passed to error messages.
        objs_keys (list): Keys to use for indexing objs_master if type(objs_master) is dict
    Returns: 
        objs_return (list): Plotted object(s) of type requested.
    """
    if(objs is None):
        # If objs_props is defined then properties are being accessed with setter functions
        if(objs_props):
            print("InputError: Trying to set {0} properties but no {0}s were specified.".format(objs_name))
        # If objs_props is False then properties are being accessed with getter functions
        elif(objs_props is False):
            print("InputError: Trying to get {0} properties but no {0}s were specified.".format(objs_name))
        return None
    elif(objs == 'all'):
        objs = objs_master  # Set objects to master list (i.e. all objects)
    # Check if properties have been set
    if(objs_props is None):
        print("InputError: Trying to set {0} properties but no properties were specified.".format(objs_name))
        return None
    # Parse input and add appropriate plot objects to list
    objs_return = []

    assert objs_keys is None or isinstance(objs_keys, list)

    # Convert object and master list to iterables
    objs = utils.get_iterable(objs)
    if(objs_keys):
        # Convert master object dictionary to list in same order as keys specified
        objs_master = [objs_master[k] for k in utils.get_iterable(objs_keys)]
    for wo in objs:
        if(isinstance(wo, int)):
            objs_return.append(objs_master[wo])
        elif(isinstance(wo, str)):
            # If input is all numbers and '-'/':'/',' then parse input into index ranges
            if(all([(c.isdigit() or c in [':', '-', ',']) for c in wo])):
                try:
                    indexes = utils.parse_str_ranges(wo)
                    for i in indexes:
                        try:
                            print(wo, indexes, objs_master[i])
                            objs_return.append(objs_master[i])
                        except IndexError as e:
                            print("IndexError: input index '{}' exceeds {} list with length of {}."
                                  .format(i, objs_name, len(objs_master)))
                            return None
                except ValueError as e:
                    print("ValueError: {}".format(str(e)))
                    return None
            # Otherwise use input as key in master list
            else:
                try:
                    objs_return.append(objs_master[objs_keys.index(wo)])
                except ValueError:
                    print("ValueError: only '{}' and 'all' are accepted object name inputs.".format("', '".join(objs_keys)))
                    return None
        elif(isinstance(wo, tuple([type(om) for om in objs_master]))):
            objs_return.append(wo)
        else:
            print("InputError: unrecognised object '{}'".format(wo))
    return objs_return


def _get_marker_paths(symbols, top_level=True):
    """Get marker path objects from symbols specified.
    Args:
        symbols (list[str]): Marker symbol names (e.g. 'x', 'o', '$word$ etc.).
        top_level: Paths objects is converted to list if True as built-in matplotlib function takes iterable input.

    Returns:
        paths (matplotlib.collections.PathCollection)
    """
    paths = symbols
    for i, s in enumerate(symbols):
        if(isinstance(s, list)):
            m = _get_marker_paths(s, False)
        else:
            # Convert string into marker object
            m = matplotlib.markers.MarkerStyle(s)
            # Convert marker object to path object and transform to figure coords
            if(top_level):
                # Convert to list if this is the list top level as each input to markers set_paths() must be list or tuple
                paths[i] = [m.get_path().transformed(m.get_transform())]
            else:
                paths[i] = m.get_path().transformed(m.get_transform())
    return paths


def _get_frame_props(legend, frame_props, var_name, private=False):
    try:
        var = getattr(legend, '_' + var_name if private else var_name)
    except AttributeError as e:
        print("Can not access private variable '{0}'. Matplotlib may have been updated and changed this variable. "
                  "If you want to change legend properties then the variable '{1}' must now be given in 'frame_props'."
              .format(re.findall("'_.+'", e.args[0])[-1]), var_name)
        return None

    if(frame_props):
        return frame_props.get(var_name, var)
    else:
        return var


def _get_props(ax, objs, objs_master, objs_name, objs_keys=None, get_ticks=None):
    """Get plotted object properties.
    Args:
        objs (int|str|matplotlib objects): Object index(es).
            Input is parsed within _get_plot_objects.
        objs_master (list): Master list of objects used to get objects when given integer indexes.
        objs_name (str): Name of object to be passed to error messages.
        objs_keys (list): Keys to use for indexing objs_master and ordering objs if type(objs_master) is dict
        get_ticks (str): Objects are ticks if defined as tick type ('major'|'minor') so get properties using built-in
            matplotlib tick keys-values getter function, otherwise if undefined get properties using built-in matplotlib
            property getter function.
    Returns:
        objs_props (dict): Properties for plotted object(s) requested. This is returned as a nested dictionary so
            that each object is clearly listed and the user can parse output as desired.
    """
    # Get appropriate objects from input as list - if objs_keys is defined get objects in order specified by objs_keys
    objs = _get_plot_objects(objs, False, objs_master,
                                      objs_name, objs_keys)
    # Get attribute name from stripped down object name that is used for error messages
    defaults_attr_name = re.sub('legend | collection', '', objs_name)+'s_props'
    # Get list of attributes to retrieve for object using defaults.json file
    objs_attrs = list(DotDict(_load_defaults())[defaults_attr_name].keys())
    # Fix attribute names used as output keys from user-friendly defaults.json names to those that matplotlib uses
    # internally
    if('symbols' in objs_attrs):
        objs_attrs[objs_attrs.index('symbols')] = 'paths'
    # Fix copied attribute names used for property access from user-friendly defaults.json names to those that
    # matplotlib uses internally - NONE DEFINED SO FAR
    objs_attrs_proper = objs_attrs.copy()  # Copy legend attributes
    if('direction' in objs_attrs):
        objs_attrs_proper[objs_attrs_proper.index('direction')] = 'tickdir'
    objs_props = {}
    # Iterate through objects
    for i, wo in enumerate(objs):
        if(objs_keys):
            key_name = objs_keys[i]
        else:
            key_name = i
        # Add to property dictionary using built in getter functions for matplotlib object and user-friendly attribute
        # names
        if(get_ticks):
            objs_props[key_name] = {objs_attrs[objs_attrs_proper.index(k)]: v for k, v in _get_tick_props(wo, get_ticks).items() if k in objs_attrs_proper}
        else:
            objs_props[key_name] = {n: plt.getp(wo, k) for k, n in zip(objs_attrs_proper, objs_attrs)}  # Add property to key name list
    return objs_props


def _get_tick_props(axes, tick_type):
    """Get tick properties. Uses private variables that may become deprecated.
    Args:
        axes:
        tick_type (str): 'major' or 'minor'.
    Returns:
        tick_props (dict): Properties for ticks requested.
    """
    try:
        if(tick_type == 'major'):
            tick_props = axes._major_tick_kw
        elif(tick_type == 'minor'):
            tick_props = axes._minor_tick_kw
        else:
            raise ValueError("Unrecognised tick type. Only 'major' or 'minor are allowed.")
    except AttributeError as e:
        print("Can not access private variable '_major_tick_kw'. Matplotlib may have been updated and changed this "
              "variable. Getting major tick properties is no longer possible.".format(re.findall("'_.+'", e.args[0])[-1]))
        return None
    else:
        return tick_props



# PRIVATE SETTER FUNCTIONS --------------------------------------------------------------------------------------------



def _set_figure_size(fig, fig_width, fig_height):
    """Set figure size in inches.
    Args:
        fig (matplotlib.figure.Figure): Figure object.
        fig_width (float):
        fig_height (float):
    Returns:
        None
    """
    fig.set_size_inches(fig_width, fig_height, forward=True)  # Force update


def _set_params_defaults(defaults, num_cols):
    """
    Args:
        defaults (DotDict): Dictionary of default plotting parameters that supports dot notation.
        num_cols (int): Number of columns the figure will span in article.
    Returns:
        defaults (DotDict): Dictionary of  updated default plotting parameters that supports dot notation.

    """
    defaults['line_width'] = 1.25 + ((num_cols - 1) * 0.5)
    defaults['marker_size'] = 30 + ((num_cols - 1) * 20)
    defaults['spine_width'] = defaults['line_width']
    defaults['label_size'] = 20 + ((num_cols - 1) * 6)
    defaults['ticklabel_size'] = 14 + ((num_cols - 1) * 4)
    defaults['texts_size'] = 18 + ((num_cols - 1) * 4)
    defaults['legendtext_size'] = 16 + ((num_cols - 1) * 4)

    return defaults


def _set_rcparams_defaults(defaults_dict):
    """Set default matplotlib.rcParams that define how the figure is rendered.
    Args:
        defaults (DotDict): Dictionary of default plotting parameters that supports dot notation.
    Returns:
        None
    """
    rcParams = matplotlib.rcParams
    rcParams['axes.unicode_minus'] = defaults_dict.use_unicode_minus  # use smaller minus sign in plots
    rcParams['axes.formatter.use_mathtext'] = defaults_dict.use_mathtext  # use mathtext for scientific notation
    rcParams['figure.dpi'] = defaults_dict.dpi


def _set_props(objs, objs_name, set_ticks=None, **kwargs):
    """Set plotted object properties.
    Args:
        objs (list): Object(s) to apply property changes to.
        objs_name (str): Name of object to be passed to error message.
        set_ticks (str): Objects are ticks if defined as tick type ('major'|'minor') so set properties using matplotlib
            built-in tick parameter setter function, otherwise if undefined set properties using built-in matplotib
            property setter function.
        **kwargs: Properties to set.
    Returns:
        None
    """
    # Remove empty keys to avoid trying to set plot parameters to None
    kwargs = utils.remove_empty_keys(kwargs)
    for k in kwargs:
        v = kwargs.get(k)
        # Convert non-iterable into list of same length as objects because this property will be applied to all objects
        if(not isinstance(v, (list, tuple))):
            kwargs[k] = [v] * len(objs)
        else:
            if(len(v) < len(objs)):
                kwargs[k] = utils.map_array(v, len(objs))
                warnings.warn("Too few arguments ({3}) set for {0} {1} property. Attempting to map input {1} properties"
                              " to all {0} objects ({2}).".format(objs_name, k, len(objs), len(v)))
        # Set each property for each appropriate object
        for w, kv in zip(objs, kwargs.get(k)):
            if(set_ticks):
                w.set_tick_params(set_ticks, **{k: kv})
            else:
                plt.setp(w, **{k: kv})



# PRIVATE MISCELLANEOUS FUNCTIONS ---------------------------------------



def _write_defaults(defaults, file='defaults.json'):
    """Write default pyblish plot parameters to json file.
    Args:
        defaults (dict): Dictionary of default plot parameters.
        file (str): File where defaults are stored in json format.
    Returns:
        None
    """
    with open(file, 'w') as fp:
        json.dump(defaults, fp, indent=4, sort_keys=True)

def _load_defaults(file='defaults.json'):
    """Load default pyblish plot parameters.
    Args:
        file (str): File where defaults are stored in json format.
    Returns:
        data (dict): Default parameters.
    """
    with open(file, 'r') as fp:
        data = json.load(fp)
    return data


def _append_log_text(wa):
    ''''''
    label_text = wa.get_label_text()
    if('log' not in label_text):
        # Check if $ at start and end of text because then it's mathtext
        if(label_text.startswith('$')):
            try:
                # Store mathtext immediately after '$' if it exists
                math_text = re.findall('\$\\\+\w+\{', label_text)[0]
            except IndexError:
                math_text = ''
            finally:
                # Add log to label with a mathtext space ('\ ')
                label_text = math_text + 'log\ ' + label_text[len(math_text):]
        else:
            label_text = 'log ' + label_text
        wa.set_label_text(label_text)


def _check_mathtext(ax, fontname):
    ''''''
    # Rework this to check label text for mathtext

    # # Check for math text anywhere in the axis object children as custom fonts won't work in this case
    # for t in [t.get_text() for t in ax.texts] + [ax.get_xlabel(), ax.get_ylabel()]:
    #     for font in utils.get_iterable(fontname):
    #         if('$' in t and font is not None):
    #             if(set_font(font, mathtext=True)):
    #                 warnings.warn("Text contains '$' so mathtext font has been custom updated to specified font. "
    #                           "This will change the appearance of all mathtext.\n"
    #                           "If you do not want this change run reset_mathtext_font() to revert back to default, "
    #                           "do not use a custom font, or remove all of the mathtext.")
    for font in utils.get_iterable(fontname):
        print(font)
