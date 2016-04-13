#!/usr/bin/python

#from __future__ import print_function

import warnings

import math
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.ticker import FuncFormatter
from fuzzywuzzy import process
import functools
import json
import re

from utils import utils

# ToDo: Main

# Add function to set axes scale and ticklabel notation


# Compact docstrings? using [%(str)] % {str='whatevs'}
# Move get & set functions next to each other?

# Remove DotDict?

# add custom exceptions to get functions?
# add custom exceptions to set functions?
# add exceptions to utils

# set custom colour cycle for lines to nice sequence - integrate ColorMapper module as utils package

spines_default_order = ['left', 'bottom', 'right', 'top']
ticks_default_order = ['x', 'y']
labels_default_order = ['x', 'y']

class InputError(Exception):
    pass


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
                   which_frames='all',
                   change_log_scales=True):

    # Convert dictionary to DotDict- a dict wrapper that allows dot notation
    defaults_dict = DotDict(_load_defaults())
    # Set defaults that are dependent on number of columns requested
    defaults_dict = _set_params_defaults(defaults_dict, num_cols)
    # Override a selection of default rcParams
    _set_rcparams_defaults(defaults_dict)
    # Set font
    set_font(defaults_dict.font)
    # Set mathtext font
    set_font(defaults_dict.font_mathtext, mathtext=True)

    # Convert aspect variable to number
    aspect = _get_aspect(aspect)
    # Set figure size
    fig_width, fig_height = _get_figure_size(num_cols, aspect)
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
                    fontsize=[defaults_dict.label_size*3, 20], fontname=defaults_dict.font, color=None))
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
        # Set line and legend line properties using default line properties
        if(which_lines):
            default_line_props = {'linewidth': defaults_dict.line_width*5,
                                  'linestyle': '-',
                                  'color': defaults_dict.col_cycle}
            set_line_props(ax, [0,1], line_props=default_line_props)
            set_line_props(ax, 'all', line_props=default_line_props, legend_lines=True)
        # Set marker and legend marker properties using default marker properties
        if(which_markers):
            default_marker_props=dict(
                        sizes=[[100, 50, 200], 400],#defaults_dict.marker_size,
                        linewidth=defaults_dict.line_width*2, linestyle=[['-', ':'], ['-', ':']],
                        facecolor=['red', 'green'], edgecolor=[defaults_dict.col_cycle]*2,
                        symbols=['x', 'x'])
            set_marker_props(ax, 'all', marker_props=default_marker_props)
            set_marker_props(ax, 'all', marker_props=default_marker_props, legend_markers=True)
        # Set text properties using default text properties
        if(which_texts):
            default_text_props=dict(
                    fontsize=defaults_dict.texts_size, fontname=defaults_dict.font,
                    color='green')
            set_text_props(ax, 'all', text_props=default_text_props)
        # Set legend text properties using default legend text properties
        # (Legend text is not related to plot text as with lines and markers)
        set_text_props(ax, 'all', text_props={'fontsize': 5}, legend_texts=True)

        # Set legend properties using default legend properties
        # Add multiple legend support?
        if(which_frames):
            set_legend_props(ax, '1', legend_props={'frameon': True, 'handlelength': 2,
                                                    'bbox_to_anchor': (0.5, 0.9, 0, 0)})
        # Set axes log scale properties
        if(change_log_scales):
            set_axes_scale(ax, 'y', {'scale': 'log', 'basex': 5, 'basey': 5}, ticklabel_exponents=True) # Integrate these two functions??
            # set_logarithmic_ticklabels(ax, 'all', base = 5)



# GETTER FUNCTIONS ----------------------------------------------------------------------------------------------------



def get_spine_props(ax, which_spines):
    """Get properties of spines. The properties are returned in the order specified. If 'all' is given instead of an
    order then the spine properties are returned in the default order: 'left', 'bottom', 'right', 'top'.
    Args:
        ax (matplotlib.axes): Axis object.
        which_spines (int|str|matplotlib.spines.Spine): Spine index(es).
            Given as a specified type OR list of a specified type.
            Names accepted are 'left', 'bottom', 'right', 'top', or 'all' can be used to select all spines.
            Comma-colon separated strings can be used to select axes in 'left', 'bottom', 'right', 'top' order.
                e.g. '0' = 'left', '0,1' = 'left, bottom', '1:3' = 'bottom, right, top'
    Returns:
        (dict): Spine properties for each spine specified (e.g. 'left', 'bottom', 'right', 'top') as a nested dictionary.
    """
    defaults = DotDict(_load_defaults())
    return _get_props(ax, which_spines, ax.spines, 'spine', list(defaults.spine_props.keys()), defaults.spine_order)


def get_tick_props(ax, which_axes, tick_type='major'):
    """Get properties of ticks. The properties are returned in the order specified. If 'all' is given instead of an
    order then the tick properties are returned in the default order: 'x', 'y'. Uses custom logic specifically for ticks as
    they are not gettable in the same way as other matplotlib objects.
    Args:
        ax (matplotlib.axes): Axis object.
        which_axes (int|str|matplotlib.axis.(XAxis|YAxis)): Axes index(es).
            Given as a specified type OR list of a specified type.
            Names accepted are 'x' or 'y', or 'all' can be used to select both axes.
            Comma-colon separated strings can be used to select axes in 'x', 'y' order.
                e.g. '0' = 'x', '0,1' = 'x, y'
        tick_type (str): 'major' or 'minor'.
    Returns:
        (dict): Tick properties for each set of ticks specified (e.g. 'x', 'y') as a nested dictionary.
    """
    defaults = DotDict(_load_defaults())
    return _get_props(ax, which_axes, {'x': ax.xaxis, 'y': ax.yaxis}, 'tick', list(defaults.tick_props.keys()),
                      defaults.tick_order, tick_type)


def get_label_props(ax, which_axes):
    """Get properties of labels. The properties are returned in the order specified. If 'all' is given instead of an
    order then the label properties are returned in the default order: 'x', 'y'.
    Args:
        ax (matplotlib.axes): Axis object.
        which_axes (int|str|matplotlib.axis.(XAxis|YAxis)): Axes index(es).
            Given as a specified type OR list of a specified type.
            Names accepted are 'x' or 'y', or 'all' can be used to select both axes.
            Comma-colon separated strings can be used to select axes in 'x', 'y' order.
                e.g. '0' = 'x', '0,1' = 'x, y'
    Returns:
        (dict): Label properties for each label specified (e.g. 'x', 'y') as a nested dictionary.
    """
    defaults = DotDict(_load_defaults())
    return _get_props(ax, which_axes, {'x': ax.xaxis.label, 'y': ax.yaxis.label}, 'label',
                      list(defaults.label_props.keys()), defaults.labels_order)


def get_line_props(ax, which_lines, legend_lines=False):
    """Get properties of lines. The properties are returned in the order specified. If 'all' is given instead of an
    order then the line properties are returned in the default order: '0', '1', '2' etc.
    Args:
        ax (matplotlib.axes): Axis object.
        which_lines (int|str|matplotlib.lines.Line2D): Line index(es).
            Given as a specified type OR list of a specified type.
            'all' can be used to select all lines.
            Comma-colon separated strings can be used to select lines in plotted order.
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
    defaults = DotDict(_load_defaults())
    return _get_props(ax, which_lines, lines_master, lines_name, list(defaults.line_props.keys()))


def get_marker_props(ax, which_markers, legend_markers=False):
    """Get properties of marker collections. The properties are returned in the order specified. If 'all' is given instead of an
    order then the marker collection properties are returned in the default order: '0', '1', '2' etc.
    Args:
        ax (matplotlib.axes): Axis object.
        which_markers (int|str|matplotlib.collections.PathCollection): Marker collection/set index(es).
            Given as a specified type OR list of a specified type.
            'all' can be used to select all marker collections.
            Comma-colon separated strings can be used to select marker collections in plotted order.
                e.g. '0' = '1st marker col', '0,1' = '1st, 2nd marker col', '1:3' = '2nd, 3rd, 4th marker col'
        legend_markers (bool): Sets properties for legend markers if True, otherwise sets properties for markers plotted
            on specified axis object.
    Returns:
        (dict): Marker properties for each marker collection specified (e.g. '0', '1', 'all') as a nested dictionary.
    """
    if(legend_markers):
        # Get appropriate markers from legend handles
        markers_master = [h for h in ax.legend_.legendHandles if isinstance(h, matplotlib.collections.PathCollection)]
        markers_name = 'legend marker collection'
    else:
        markers_master = ax.collections
        markers_name = 'marker collection'
    defaults = DotDict(_load_defaults())
    marker_props = _get_props(ax, which_markers, markers_master, markers_name, list(defaults.marker_props.keys()))
    # Convert sizes output into nested lists
    marker_props['sizes'] =  [list(x) for x in marker_props['sizes']]
    return marker_props

def get_text_props(ax, which_texts, legend_texts=False):
    """Get properties of texts. The properties are returned in the order specified. If 'all' is given instead of an
    order then the text properties are returned in the default order: '0', '1', '2' etc.
    Args:
        ax (matplotlib.axes): Axis object.
        which_texts (int|str|matplotlib.texts.text2D): text index(es).
            Given as a specified type OR list of a specified type.
            'all' can be used to select all texts.
            Comma-colon separated strings can be used to select texts in plotted order.
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
    defaults = DotDict(_load_defaults())
    return _get_props(ax, which_texts, texts_master, texts_name, list(defaults.text_props.keys()))


def get_legend_props(ax, which_legends):
    """Get properties of legend. The legend properties are returned in the order specified. If 'all' is given instead
    of an order then the properties are returned in the default order: '0', '1', '2' etc.
    All additional legends added via plt.gca().add_artist are automatically processed by default, or can be specified
    using indexes >=1 (0 = native axis legend).
    Args:
        ax (matplotlib.axes): Axis object.
        ****** replace objs with legends and add support for multiple legends
        which_legends (int|str|matplotlib.legend.Legend): Legend index(es).
            Given as a specified type OR list of a specified type.
            'all' can be used to select all objects.
            Comma-colon separated strings can be used to select objects in plotted order.
                e.g. '0' = '1st legend', '0,1' = '1st, 2nd legend', '1:3' = '2nd, 3rd, 4th legend'
        *******
    Returns:
        (dict): text properties for each text specified (e.g. '0', '1', 'all') as a nested dictionary.
    """
    # Get master list of all legends in plot including additional legends added via add_artist
    legends_master = [ax.legend_]
    legends_master.extend([l for l in ax.artists if isinstance(l, matplotlib.legend.Legend)])

    which_legends = _get_plot_objects(which_legends, True, legends_master, 'legend')

    defaults = DotDict(_load_defaults())
    legend_props = _get_props(ax, which_legends, legends_master, 'legend', list(defaults.legend_props.keys()))
    # Convert bbox output into tuple (x0, y0, width, height) coords
    legend_props['bbox_to_anchor'] = [_bbox_to_coords(ax, bbox) for bbox in legend_props['bbox_to_anchor']]
    return legend_props


@functools.lru_cache(2)
def get_available_fonts():
    """Use matplotlib.font_manager to get fonts on system.
    Returns:
         Alphabetically sorted list of .ttf font names.
    """
    FM = fm.FontManager()
    font_names = set([f.name for f in FM.ttflist])
    return sorted(font_names)


def get_available_linestyles():
    """Get linestyles accepted by matplotlib.lines.Line2D objects.
    Returns:
        Available linestyles.
    """
    return ['solid: "-"', 'dashed: "--"', 'dashed-dotted: "-."', 'dotted: ":"', 'custom sequence: "(on, off)"']


def print_available_fonts():
    _print_availables(get_available_fonts)

def print_available_linestyles():
    _print_availables(get_available_linestyles)




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
    default_attr = '_mathtext' if mathtext else ''
    font = _get_system_font(font, _load_defaults()['font' + default_attr])
    if(font):
        if(mathtext):
            # Check if font is one of the 3 global fontsets
            if(font in ['cm', 'sans', 'stixsans']):
                matplotlib.rcParams['mathtext.fontset'] = font
            else:
                matplotlib.rcParams['mathtext.fontset'] = 'custom'
                matplotlib.rcParams['mathtext.cal'] = font
                matplotlib.rcParams['mathtext.rm'] = font
                matplotlib.rcParams['mathtext.tt'] = font
                matplotlib.rcParams['mathtext.sf'] = font
        else:
            matplotlib.rcParams['font.family'] = font


def get_font(mathtext=False):
    """Get plot font (normal or mathtext). The method for setting mathtext is experimental and may be removed in future
    updates to matplotlib.
    Args:
        mathtext (bool): Sets mathtext rather than normal plot text if True.
    Returns:
        (str): matplotlib.rcParams font parameter.
    """
    if(mathtext):
        if(matplotlib.rcParams['mathtext.fontset'] == 'custom'):
            return matplotlib.rcParams['mathtext.rm']
        else:
            return matplotlib.rcParams['mathtext.fontset']
    else:
        return matplotlib.rcParams['font.family'][0]  # font.family is converted to list in built-in matplotlib function


def get_default(attr):
    return _load_defaults()[attr]


def set_spine_props(ax, which_spines, spine_props, hide_other_spines=True, duplicate_ticks=False):
    """Set properties of spines.
    Args:
        ax (matplotlib.axes): Axis object.
        which_spines (int|str|matplotlib.spines.Spine): Spine index(es).
            Given as a specified type OR list of a specified type.
            Names accepted are 'left', 'bottom', 'right', 'top', or 'all' can be used to select all spines.
            Comma-colon separated strings can be used to select axes in 'left', 'bottom', 'right', 'top' order.
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
        which_axes (int|str|matplotlib.axis.(XAxis|YAxis)): Axes index(es).
            Given as a specified type OR list of a specified type.
            Names accepted are 'x' or 'y', or 'all' can be used to select both axes.
            Comma-colon separated strings can be used to select axes in 'x', 'y' order.
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
        raise InputError("Tick type not recognised. Enter 'major' or 'minor'.")
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
        which_axes (int|str|matplotlib.axis.(XAxis|YAxis)): Axes index(es).
            Given as a specified type OR list of a specified type.
            Names accepted are 'x' or 'y', or 'all' can be used to select both axes.
            Comma-colon separated strings can be used to select axes in 'x', 'y' order.
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
            Comma-colon separated strings can be used to select lines in plotted order.
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
            Comma-colon separated strings can be used to select marker collections in plotted order.
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
            Comma-colon separated strings can be used to select texts in plotted order.
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
        texts_name = 'text'
    # Get appropriate text object(s) from input as list
    which_texts = _get_plot_objects(which_texts, text_props, texts_master,
                                     texts_name)
    if(which_texts):
        if('fontname' in text_props):
            if(legend_texts):
                warnings.warn("Legend font can not be changed this way as it is rendered as mathtext. "
                          "Use set_font('font', mathtext=True) to set the mathtext font within the plot instead.")
            else:
                text_props['fontname'] = _get_system_font(text_props['fontname'], _load_defaults()['font'])
                if(text_props['fontname']):
                    _check_for_mathtext(which_texts, text_props['fontname'], texts_name)
        if('fontsize' in text_props and legend_texts):
            # More than one fontsize is not supported in legend text
            if(len(set(utils.get_iterable(text_props['fontsize']))) > 1):
                warnings.warn("Only one fontsize can be used in legend text.")
        # Set properties using matplotlib.pyplot.setp
        _set_props(which_texts, texts_name, **text_props)


def set_legend_props(ax, which_legends='all', legend_props=None):
    """Set properties for legends.
    Args:
        ax (matplotlib.axes): Axis object.
        which_legends (int|str|matplotlib.legend.Legend): Legend index(es).
            Given as a specified type OR list of a specified type.
            'all' can be used to select all objects.
            Comma-colon separated strings can be used to select objects in plotted order.
                e.g. '0' = '1st legend', '0,1' = '1st, 2nd legend', '1:3' = '2nd, 3rd, 4th legend'
        legend_props (dict): Legend properties. See matplotlib.legend documentation for full properties list.
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
    # Get master list of all legends in plot including additional legends added via add_artist
    legends_master = [ax.legend_]
    legends_master.extend([l for l in ax.artists if isinstance(l, matplotlib.legend.Legend)])

    which_legends = _get_plot_objects(which_legends, legend_props, legends_master, 'legend')
    
    if(which_legends):
        # Update legend attribute names to those used for matplotlib legend object
        for n, k in zip(['bbox_to_anchor', 'loc', 'ncol', 'frameon'],
                        ['_bbox_to_anchor', '_loc', '_ncol', '_drawFrame']):
            if(n in legend_props):
                # Convert (x0, y0, (width, height))tuple|list into Bbox object
                if(n == 'bbox_to_anchor'):
                    legend_props[n] = _get_legend_bboxes(ax, legend_props[n])
                legend_props[k] = legend_props[n]
                legend_props.pop(n)  # Remove user-friendly names
        # Position updated legend in same location as previous if bbox_to_anchor is not specified
        if('_bbox_to_anchor' not in legend_props):
            legend_props['_bbox_to_anchor'] = [wl.get_bbox_to_anchor() for wl in which_legends]
        _set_props(which_legends, 'legend', redraw=False, **legend_props)
        # Update legend artists to reflect changes
        legend_artists = [wl for wl in which_legends]
        plt.gca().artists = list(set(plt.gca().artists) | set(legend_artists))


# Allow setting of arbitrary axes scale - eg: log, ^2 etc.
def set_axes_scale(ax, which_axes, scale_props={'scale': 'log', 'base': 10.0}, ticklabel_exponents=False, add_log=True):
    """
    Args:
        ax (matplotlib.axes): Axis object.
        which_axes (int|str|matplotlib.axis.(XAxis|YAxis)): Axes index(es).
            Given as a specified type OR list of a specified type.
            Names accepted are 'x' or 'y', or 'all' can be used to select both axes.
            Comma-colon separated strings can be used to select axes in 'x', 'y' order.
                e.g. '0' = 'x', '0,1' = 'x, y'
        scale (str): 'log', 'linear', 'symlog' or 'logit'. See matplotlib documentation for an explanation.
        base (int): Logarithmic base. Only used if scale = 'log'.
        ticklabel_exponents: Tick labels are converted to exponent values if True. Only used if scale = 'log'.
        add_log: 'log_base' is added to axis label if True
    Returns:
        None
    """
    # Get appropriate axis/axes objects from input as list
    which_axes = _get_plot_objects(which_axes, False, {'x': ax.xaxis, 'y': ax.yaxis},
                                    'axis', ['x', 'y'])
    scales = {'x': ax.set_xscale, 'y': ax.set_yscale}

    # Need to have array input for scales, bases etc. - hmm how to parse - need to do something like
    # in set_props but more focused
    scale = scale_props.pop('scale')
    if(which_axes):
        for i, wa in enumerate(which_axes):
            print(scale_props)
            scales[wa.axis_name](scale.lower(), **scale_props)

            # Set tick labels to exponents
            if(scale == 'log' and ticklabel_exponents):
                _set_ticklabel_exponents(wa, scale_props, add_log)


# ToDo: Any other one-off functions for adjusting plotted features?


# PRIVATE GETTER FUNCTIONS --------------------------------------------------------------------------------------------


def _get_aspect(aspect):
    """Get width-to-height figure aspect ratio given name or value input.
    Args:
        aspect (str|float): Width-to-height figure aspect ratio name or width:height value.
    Returns:
        aspect_return (float): Width-to-height figure aspect ratio.
    """
    aspect_dict = {'square': 1, 'normal': 1.333, 'golden': 1.618, 'widescreen': 1.78}
    if(isinstance(aspect, (float, int))):
        aspect_return = aspect
    elif(isinstance(aspect, str)):
        # Convert aspect into a width:height fraction
        if(':' in aspect):
            numerator, denominator = aspect.split(':')
            aspect_return = float(numerator)/float(denominator)
        # Convert aspect into a width/height fraction from preset dict
        elif(aspect in aspect_dict):
            aspect_return = aspect_dict[aspect]
        else:
            raise InputError("Unrecognised aspect name. Accepted names are '{}'."
                             .format("', '".join(aspect_dict.keys())))
    else:
        raise InputError("Unrecognised aspect value. Accepted inputs are '{}', a 'width:height' ratio or width/height "
                         "fraction.".format("', '".join(aspect_dict.keys())))
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
        objs_master (list|dict): Used to retrieve correct object given int|str input. If dict type then it is converted
        to a list of values in order specified in objs_keys.
        objs_name (str): Name of object to be passed to error messages.
        objs_keys (list): Keys to use for indexing objs_master if type(objs_master) is dict
    Returns: 
        objs_return (list): Plotted object(s) of type requested.
    """
    if(objs is None):
        # If objs_props is defined then properties are being accessed with setter functions
        if(objs_props):
            raise InputError("Trying to set {0} properties but no {0}s were specified.".format(objs_name))
        # If objs_props is False then properties are being accessed with getter functions
        elif(objs_props is False):
            raise InputError("Trying to get {0} properties but no {0}s were specified.".format(objs_name))
    elif(objs == 'all'):
        objs = objs_master  # Set objects to master list (i.e. all objects)
    # Check if properties have been set
    if(objs_props is None):
        raise InputError("Trying to set {0} properties but no properties were specified.".format(objs_name))
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
            wo = wo.replace(' ', '')
            if(all([(c.isdigit() or c in [':', '-', ',']) for c in wo])):
                try:
                    indexes = utils.parse_str_ranges(wo)
                    for i in indexes:
                        try:
                            objs_return.append(objs_master[i])
                        except IndexError as e:
                            raise InputError("Input index '{}' exceeds {} list with length of {}."
                                  .format(i, objs_name, len(objs_master)))
                except ValueError as e:
                    raise InputError("{}".format(str(e)))
            # Otherwise use input as key in master list
            else:
                try:
                    objs_return.append(objs_master[objs_keys.index(wo)])
                except ValueError:
                    raise InputError("Only '{}' and 'all' are accepted object name inputs.".format("', '".join(objs_keys)))
        elif(isinstance(wo, tuple([type(om) for om in objs_master]))):
            objs_return.append(wo)
        else:
            raise InputError("Unrecognised object '{}'".format(wo))
    return objs_return


def _get_marker_paths(symbols, top_level=True):
    """Get marker path objects from symbols specified recursively.
    Args:
        symbols (list[str]): Marker symbol names (e.g. 'x', 'o', '$word$ etc.).
        top_level: Paths objects is converted to list if True as built-in matplotlib function takes iterable input.
    Returns:
        paths (matplotlib.collections.PathCollection)
    """
    assert isinstance(symbols, list)
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


def _get_legend_bboxes(ax, coords):
    """Get Bbox object from axis coordinates recursively. Input can be tuple or bbox object, or a list of the
    aforementioned. If a tuple is encountered it is assumed to be bbox coords and converted into a Bbox object.
    Args:
        ax (matplotlib.axes): Axis object.
        coords (tuple|bbox object|list: Coordinates of bbox in axis space.
    Returns:
    """
    if(isinstance(coords, tuple)):
        coords = _coords_to_bbox(ax, coords)
    elif(isinstance(coords, list)):
        for i, c in enumerate(coords):
            coords[i] = _get_legend_bboxes(ax, c)
    elif(isinstance(coords, matplotlib.transforms.TransformedBbox)):
        pass
    else:
        print("Unrecognised value for bbox_to_anchor. Valid inputs are bbox objects, tupls, or list of tuples|bbox objects.")

    return coords


def _get_system_font(font, default_font):
    """Get name of font on system by taking the closest match between font specified and fonts on system.
    Args:
        font (str): Font name.
    Returns:
        font (str): Font name as it is defined on system.
    """
    # Check if font is one of the 3 global fontsets
    if(font in ['sans', 'stixsans', 'cm']):
        return font
    else:
        fonts = get_available_fonts()
        # Compare font to fonts and extract best match if minimum score exceeded
        font_found = process.extractOne(font, fonts, score_cutoff=80)
        if(font_found):
            return font_found[0]
        else:
            warnings.warn("'{}' font not found. Use get_available_fonts() or print_available fonts() to see fonts "
                  "installed on this system. Reverting back to default '{}' font.".format(font, default_font))
            return None


def _get_props(ax, objs, objs_master, objs_name, objs_attrs, objs_keys=None, get_ticks=None):
    """Get plotted object properties.
    Args:
        objs (int|str|matplotlib objects): Object index(es).
            Input is parsed within _get_plot_objects.
        objs_master (list|dict): Used to retrieve correct object indexes.
        objs_name (str): Name of object to be passed to error messages.
        objs_keys (list): Keys to use for indexing objs_master and ordering objs if type(objs_master) is dict
        get_ticks (str): Objects are ticks if defined as tick type ('major'|'minor') so get properties using built-in
            matplotlib tick keys-values getter function, otherwise if undefined get properties using getattr.
    Returns:
        objs_props (dict): Properties for plotted object(s) requested. This is returned as a nested dictionary so
            that each object is clearly listed and the user can parse output as desired.
    """
    # Get appropriate objects from input as list - if objs_keys is defined get objects in order specified by objs_keys
    objs = _get_plot_objects(objs, False, objs_master,
                                      objs_name, objs_keys)
    # Fix attribute names used only as output keys from user-friendly defaults.json names to those that matplotlib uses
    # internally and which are more appropriate for output
    if('symbols' in objs_attrs):
        objs_attrs[objs_attrs.index('symbols')] = 'paths'
    # Fix copied attribute names used only for property access from user-friendly defaults.json names to those that
    # matplotlib uses internally
    objs_attrs_proper = objs_attrs.copy()  # Copy legend attributes
    if(objs_name == 'tick'):
        objs_attrs_proper[objs_attrs_proper.index('direction')] = 'tickdir'
    if(objs_name == 'legend'):
        objs_attrs_proper[objs_attrs_proper.index('loc')] = '_loc'
        objs_attrs_proper[objs_attrs_proper.index('ncol')] = '_ncol'
        objs_attrs_proper[objs_attrs_proper.index('frameon')] = '_drawFrame'
        objs_attrs_proper[objs_attrs_proper.index('bbox_to_anchor')] = '_bbox_to_anchor'

    objs_props = {}
    # Iterate through object attributes and add to property dictionary using built in getter functions for matplotlib
    # object and user-friendly attribute names
    for n, k in zip(objs_attrs, objs_attrs_proper):
        if(get_ticks):
            objs_props[n] = [_get_tick_props(wo, get_ticks).get(k) for wo in objs]
        else:
            objs_props[n] = [getattr(wo, k) for wo in objs]
    return objs_props


def _get_tick_props(axes, tick_type):
    """Get tick properties. Uses private variables that may become deprecated.
    Args:
        axes:
        tick_type (str): 'major' or 'minor'.
    Returns:
        tick_props (dict): Properties for ticks requested.
    """
    assert tick_type in ['major', 'minor']
    try:
        if(tick_type == 'major'):
            tick_props = axes._major_tick_kw
        elif(tick_type == 'minor'):
            tick_props = axes._minor_tick_kw
    except AttributeError as e:
        raise AttributeError("Can not access private variable '_major_tick_kw'. Matplotlib may have been updated and "
                             "changed this variable. Getting major tick properties is no longer possible."
                             .format(re.findall("'_.+'", e.args[0])[-1]))
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


def _set_ticklabel_exponents(ax, base, add_log=True):
    """Set tick labels to log_base of values, which is the exponent of the mantissa (e.g. 10^2 -> 2 in log base 10)
    Args:
        ax (matplotlib.axes): Axis object.
        base: Logarithmic base.
    Returns:
        None
    """
    try:
        # Take logarithm of tick labels
        ax.set_major_formatter(FuncFormatter(lambda x, p: "{:.2f}".format(math.log(x, base))))
    except ValueError:
        raise ValueError("Ticks must not be <= 0 in order to take logarithm.")
    else:
        if(add_log):
            # Add 'log_base' to axis label if doesn't already start with 'log'
            if not(re.sub(r'(\$)(\\?\w+{)?', '', ax.get_label_text()).startswith('log')):
                base_part = '' if base == 10 else '{}'.format(base)
                ax.set_label_text('$\mathrm{' + 'log_{%s}' % base_part + '}$ ' + ax.get_label_text())


def _set_props(objs, objs_name, set_ticks=None, redraw=True, **kwargs):
    """Set plotted object properties.
    Args:
        objs (list): Object(s) to apply property changes to.
        objs_name (str): Name of object to be passed to error message.
        set_ticks (str): Objects are ticks if defined as tick type ('major'|'minor') so set properties using matplotlib
            built-in tick parameter setter function, otherwise if undefined set properties using built-in matplotib
            property setter function.
        redraw (bool): Use plt.setp if True as this built-in matplotlib function automatically redraws the artist,
            otherwise use setattr as redrawing is handled elsewhere.
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
                if(redraw):
                    plt.setp(w, **{k: kv})  # Sets property and redraws artist
                else:
                    setattr(w, k, kv) # Sets property - redrawing is handled elsewhere



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

@functools.lru_cache(2)
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


def _check_for_mathtext(texts, font, name):
    for text in texts:
        t = text.get_text()
        # Text contains $...$
        if(re.match('(\$[^$]+\$)', t)):
            # Set mathtext font if it is not already set as the font specified and issue warning
            if not(get_font(mathtext=True) == font):
                set_font(font, mathtext=True)
                warnings.warn("'{}' {} contains mathtext so mathtext font has been changed to specified font '{}'. "
                              "This affects all mathtext in the plot, however, so use "
                              "set_font(get_default('font_mathtext'), mathtext=True) to revert this change and "
                              "remove mathtext from the text before reattempting.".format(t, name, font))


def _coords_to_bbox(ax, coords):
    """Convert coordinates to matplotlib.transforms.TransformedBbox object in axis space.

    Args:
        ax (matplotlib.axes._subplots.AxesSubplot): Axis object.
        coords (tuple): Coordinates in (x0, y0, width, height) format. Width and height are optional parameters.

    Returns:
        Bbox object at specified coords.
    """
    from matplotlib.transforms import Bbox, TransformedBbox

    if(len(coords) == 2):
        coords = [coords[0], coords[1], 0, 0]
    return TransformedBbox(Bbox.from_bounds(*coords), ax.transAxes)


def _bbox_to_coords(ax, bbox):
    """Convert matplotlib.transforms.TransformedBbox object to coordinates in axis space.

    Args:
        ax (matplotlib.axes._subplots.AxesSubplot): Axis object.
        bbox (matplotlib.transforms.TransformedBbox): Bbox object in axis space.

    Returns:
        (tuple): Coordinates of bbox in (x0, y0, width, height) format.
    """
    coords = ax.transAxes.inverted().transform(bbox.get_points())
    return (coords[0][0], coords[0][1],  coords[1][0]-coords[0][0], coords[1][1]-coords[0][1])


def _print_availables(func):
    """Print entries in list.
    Args:
        func: Function that returns list of entries.
    Returns:
        None
    """
    print('\n'.join(func()))