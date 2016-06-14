#!/usr/bin/python

# Import built-ins
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.ticker import FuncFormatter
import sys
import warnings
import functools
import json
import math

# Import externals
from fuzzywuzzy import process
from utils.converters import *
from utils.parser import *
from utils.decorator import *
from utils.availables import *
from utils.colormap import *

#ToDo: Bug-checking. Make sure pyblishify works for a range of figures!


class InputError(Exception):
    pass


def pyblishify(fig, num_cols, aspect='square', which_labels='all', which_ticks='all',
               which_spines=('left', 'bottom'),
               which_lines='all', which_markers='all', which_texts='all',
               which_legends='all',
               which_log_scales='all',
               save_file=None,
               **kwargs):

    # Get default parameters from 'defaults.json'
    defaults_dict = get_defaults('defaults.json')
    # Set default parameters that = 'master' to appropriate value from master_defaults dict
    _set_master_defaults(defaults_dict)
    # Fix default parameters and names to be consistent with matplotlib conventions
    _fix_defaults(defaults_dict)
    # Set defaults that are dependent on number of columns requested
    # defaults_dict = _set_params_defaults(defaults_dict, num_cols)
    # Override a selection of default rcParams
    _set_rcparams_defaults(defaults_dict)
    # Set font
    set_font(defaults_dict['fontname'])
    # Set mathtext font
    set_font(defaults_dict['fontname_mathtext'], mathtext=True)

    # Allow user to pass in any dictionary of properties as kwargs and take passed in values
    # or default if no value passed
    parameters_dict = _get_plot_properties(['spine_props', 'label_props', 'major_tick_props', 'minor_tick_props',
                                            'line_props', 'marker_props', 'text_props',
                                            'legend_line_props', 'legend_marker_props', 'legend_text_props',
                                            'legend_props', 'log_scale_props'],
                                           kwargs, defaults_dict)

    # Convert aspect variable to number
    aspect = _get_aspect(aspect)
    # Set figure size
    fig_width, fig_height = _get_figure_size(num_cols, aspect)
    set_figure_size(fig, fig_width, fig_height, 2.0)

    # Apply changes to all axis objects in figure
    for ax in fig.axes:
        # Set axes spine properties using default spine properties
        if(which_spines):
            set_spine_props(ax, which_spines, spine_props=parameters_dict['spine_props'],
                            hide_other_spines=True, duplicate_ticks=True)
        # Set axes ticks and ticklabel properties using default tick and ticklabel properties
        if(which_ticks):
            set_tick_props(ax, which_ticks, tick_props=parameters_dict['major_tick_props'], tick_type='major')
            set_tick_props(ax, which_ticks, tick_props=parameters_dict['minor_tick_props'], tick_type='minor')
        # Set axes label properties using default label properties
        if(which_labels):
            set_label_props(ax, which_labels, label_props=parameters_dict['label_props'])
        # Set line and legend line properties using default line properties
        if(which_lines):
            set_line_props(ax, which_lines, line_props=parameters_dict['line_props'])
            if(ax.legend_):
                set_line_props(ax, 'all', line_props=parameters_dict['legend_line_props'], legend_lines=True)
        # Set marker and legend marker properties using default marker properties
        if(which_markers):
            set_marker_props(ax, which_markers, marker_props=parameters_dict['marker_props'])
            if(ax.legend_):
                set_marker_props(ax, 'all', marker_props=parameters_dict['legend_marker_props'], legend_markers=True)
        # Set text properties using default text properties
        if(which_texts):
            set_text_props(ax, which_texts, text_props=parameters_dict['text_props'])
        # Set legend text properties using default legend text properties
        # (Legend text is not related to plot text as with lines and markers)
        if(ax.legend_):
            set_text_props(ax, 'all', text_props=parameters_dict['legend_text_props'], legend_texts=True)

        # Set legend properties using default legend properties
        if(which_legends):
            if(ax.legend_):
                set_legend_props(ax, which_legends, legend_props=parameters_dict['legend_props'])
        # Set axes log scale properties
        if(which_log_scales):
            set_log_scale(ax, which_log_scales, log_scale_props=parameters_dict['log_scale_props'])

    # Get list of legends to send to savefig as bbox_extra_artists to ensure saved figure has enough space around plot
    # for legends
    legends = get_iterable(ax.legend_) + [l for l in ax.artists if isinstance(l, matplotlib.legend.Legend)]
    if(all([l is None for l in legends])):
        legends = None
    if(save_file):
        save_figure(save_file, kwargs.pop('format', 'png'), kwargs.pop('bbox_inches', 'tight'), legends)


def make_figure(rows, cols, sharex=False, sharey=False, subplot_keywords=None, gridspec_keywords=None,
                **figure_keywords):
    """Make figure and axes objects used for plotting.
    Args:
        rows (int): Number of canvases vertically.
        cols (int): Number of canvases horizontally.
        sharex (bool): Whether to share x axis between multiple canvases.
        sharey (bool): Whether to share y axis between multiple canvases.
        subplot_keywords (dict): Keywords used for add_subplot().
        gridspec_keywords (dict): Keywords used for gridspec.GridSpec()
    Returns:
        fig (matplotlib.figure.Figure): Figure object.
        axes (matplotlib.axes._subplots.AxesSubplot): Axes object(s).
    """
    fig, axes = plt.subplots(rows, cols, sharex, sharey, subplot_keywords, gridspec_keywords, **figure_keywords)
    if(len(axes.ravel()) == 1):
        return fig, axes[0][0]
    else:
        return fig, axes


def save_figure(file_path, format='png', bbox='tight', extra_artists=None, **kwargs):
    """Save figure to file.
    Args:
        file_path (str): Path to save figure to.
        format (str): Format to save figure in.
        bbox (str):  Only the bbox specified is saved. 'tight' forces matplotlib to figure out bbox automatically.
        extra_artists (list): A list of extra artists that are considered when calculating the bbox.
    Returns:
        None
    """
    plt.savefig(file_path, format=format, bbox_inches=bbox, bbox_extra_artists=extra_artists, **kwargs)  # , bbox_extra_artists=(l,)


# PLOT OBJECT GETTER & SETTER FUNCTIONS ------------------------------------------------------------------------


def get_spine_props(ax, which_spines):
    """Get properties of spines. The properties are returned in the order specified. If 'all' is given instead of an
    order then the spine properties are returned in the default order: 'left', 'bottom', 'right', 'top'.
    Args:
        ax (matplotlib.axes): Axis object.
        which_spines (int|str|matplotlib.spines.Spine): Spine index(es) or object(s).
            Given as a specified type OR list of a specified type.
            Names accepted are 'left', 'bottom', 'right', 'top', or 'all' can be used to select all spines.
            Comma-colon separated strings can be used to select axes in 'left', 'bottom', 'right', 'top' order.
                e.g. '0' = 'left', '0,1' = 'left, bottom', '1:3' = 'bottom, right, top'
    Returns:
        (dict): Spine properties for each spine specified (e.g. 'left', 'bottom', 'right', 'top') as nested dictionary.
    """
    defaults = get_defaults()
    defaults['spine_props'] = _fix_props(defaults['spine_props'], 'spine')
    return _get_props(which_spines, ax.spines, 'spine', defaults['spine_props'],
                      ['left', 'bottom', 'right', 'top'])


def set_spine_props(ax, which_spines, spine_props, hide_other_spines=True, duplicate_ticks=False):
    """Set properties of spines.
    Args:
        ax (matplotlib.axes): Axis object.
        which_spines (int|str|matplotlib.spines.Spine): Spine index(es) or object(s).
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
        if(hide_other_spines):
            # Turn off all spines and ticks and tick labels
            for ax_dir in spines:
                spines[ax_dir].axis.set_tick_params(which='both', **{ax_dir: 'off'})
                # Separated from above line for python 2 compatibility
                spines[ax_dir].axis.set_tick_params(which='both', **{'label'+ax_dir: 'off'})
                spines[ax_dir].set_visible(False)
        # Show spines and ticks and ticklabels for spines specified
        for sp in which_spines:
            ax_dir = list(spines.keys())[list(spines.values()).index(sp)]
            sp.axis.set_tick_params(which='both', **{ax_dir: 'on'})
            # Separated from above line for python 2 compatibility
            sp.axis.set_tick_params(which='both', **{'label'+ax_dir: 'on'})
            sp.set_visible(True)
            if not(duplicate_ticks):
                # Set ticks only on one side, according to which 'left'|'right', 'bottom'|'top' spine is ordered last
                # in which_spines
                sp.axis.set_ticks_position(ax_dir)
        # Fix property input to be consistent with matplotlib conventions
        _fix_props(spine_props, 'spine')
        # Set properties using matplotlib.pyplot.setp
        _set_props(which_spines, 'spine', **spine_props)


def get_tick_props(ax, which_axes, tick_type='major'):
    """Get properties of ticks. The properties are returned in the order specified. If 'all' is given instead of an
    order then the tick properties are returned in the default order: 'x', 'y'. Uses custom logic specifically for
    ticks as they are not gettable in the same way as other matplotlib objects.
    Args:
        ax (matplotlib.axes): Axis object.
        which_axes (int|str|matplotlib.axis.(XAxis|YAxis)): Axes index(es) or object(s).
            Given as a specified type OR list of a specified type.
            Names accepted are 'x' or 'y', or 'all' can be used to select both axes.
            Comma-colon separated strings can be used to select axes in 'x', 'y' order.
                e.g. '0' = 'x', '0,1' = 'x, y'
        tick_type (str): 'major' or 'minor'.
    Returns:
        (dict): Tick properties for each set of ticks specified (e.g. 'x', 'y') as a nested dictionary.
    """
    defaults = get_defaults()
    _fix_props(defaults['tick_props'], 'ticks')
    return _get_props(which_axes, {'x': ax.xaxis, 'y': ax.yaxis}, 'tick', defaults['tick_props'],
                      ['x', 'y'], tick_type)


def set_tick_props(ax, which_axes, tick_props, tick_type='major'):
    """Set properties for axes ticks. Uses custom logic specifically for ticks as they are not settable in the same
    way as other matplotlib objects.
    Args:
        ax (matplotlib.axes): Axis object.
        which_axes (int|str|matplotlib.axis.(XAxis|YAxis)): Axes index(es) or object(s) or object(s).
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
        # Fix property input to be consistent with matplotlib conventions
        _fix_props(tick_props, 'ticks')
        # Set properties using ax.(x|y)axis.set_tick_params
        _set_props(which_axes, 'ticks', set_ticks=tick_type, **tick_props)


def get_label_props(ax, which_axes):
    """Get properties of labels. The properties are returned in the order specified. If 'all' is given instead of an
    order then the label properties are returned in the default order: 'x', 'y'.
    Args:
        ax (matplotlib.axes): Axis object.
        which_axes (int|str|matplotlib.axis.(XAxis|YAxis)): Axes index(es) or object(s).
            Given as a specified type OR list of a specified type.
            Names accepted are 'x' or 'y', or 'all' can be used to select both axes.
            Comma-colon separated strings can be used to select axes in 'x', 'y' order.
                e.g. '0' = 'x', '0,1' = 'x, y'
    Returns:
        (dict): Label properties for each label specified (e.g. 'x', 'y') as a nested dictionary.
    """
    defaults = get_defaults()
    _fix_props(defaults['label_props'], 'label')
    return _get_props(which_axes, {'x': ax.xaxis.label, 'y': ax.yaxis.label}, 'label',
                      defaults['label_props'], ['x', 'y'])


def set_label_props(ax, which_labels, label_props):
    """Set properties for axes labels.
    Args:
        ax (matplotlib.axes): Axis object.
        which_labels (int|str|matplotlib.text.Text): Label index(es) or object(s) or object(s).
            Given as a specified type OR list of a specified type.
            Names accepted are 'x' or 'y', or 'all' can be used to select both axes.
            Comma-colon separated strings can be used to select axes in 'x', 'y' order.
                e.g. '0' = 'x', '0,1' = 'x, y'
        label_props (dict): Label properties. Each property can be given as an appropriate type and applied to all
            labels. Alternatively, a list may be given for each property so that each label is assigned different
            properties.
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
        if('fontname' in label_props):
            # Get closest matching font or None if font not found
            label_props['fontname'] = _get_system_font(label_props['fontname'])
            # Check if label text contains mathtext and if so change the mathtext font to accommodate
            _change_mathtext(which_labels, label_props['fontname'])
        # Fix property input to be consistent with matplotlib conventions
        _fix_props(label_props, 'label')
        # Set properties using matplotlib.pyplot.setp
        _set_props(which_labels, 'label', **label_props)


def get_line_props(ax, which_lines, legend_lines=False):
    """Get properties of lines. The properties are returned in the order specified. If 'all' is given instead of an
    order then the line properties are returned in the default order: '0', '1', '2' etc.
    Args:
        ax (matplotlib.axes): Axis object.
        which_lines (int|str|matplotlib.lines.Line2D): Line index(es) or object(s).
            Given as a specified type OR list of a specified type.
            'all' can be used to select all lines.
            Comma-colon separated strings can be used to select lines in plotted order.
                e.g. '0' = '1st line', '0,1' = '1st, 2nd line', '1:3' = '2nd, 3rd, 4th line'
        legend_lines (bool): Sets properties for legend lines if True, otherwise sets properties for lines plotted on
            specified axis object.
    Returns:
        (dict): Line properties for each line specified (e.g. '0', '1', 'all') as a nested dictionary.
    """
    lines_master, lines_name = _get_master_objs(ax, 'line', matplotlib.lines.Line2D, ax.lines,
                                                legend_lines)
    defaults = get_defaults()
    # Fix default properties to be consistent with matplotlib conventions
    _fix_props(defaults['line_props'], lines_name)
    return _get_props(which_lines, lines_master, lines_name, defaults['line_props'])


def set_line_props(ax, which_lines, line_props, legend_lines=False):
    """Set properties for lines.
    Args:
        ax (matplotlib.axes): Axis object.
        which_lines (int|str|matplotlib.lines.Line2D): Line index(es) or object(s).
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
    lines_master, lines_name = _get_master_objs(ax, 'line', matplotlib.lines.Line2D, ax.lines,
                                                legend_lines)
    # Get appropriate line object(s) from input as list
    which_lines = _get_plot_objects(which_lines, line_props, lines_master, lines_name)
    if(which_lines):
        # Fix property input to be consistent with matplotlib conventions
        _fix_props(line_props, lines_name)
        # Set properties using matplotlib.pyplot.setp
        _set_props(which_lines, lines_name, **line_props)


def get_marker_props(ax, which_markers, legend_markers=False):
    """Get properties of marker collections. The properties are returned in the order specified. If 'all' is given
    instead of an order then the marker collection properties are returned in the default order: '0', '1', '2' etc.
    Args:
        ax (matplotlib.axes): Axis object.
        which_markers (int|str|matplotlib.collections.PathCollection): Marker collection/set index(es) or object(s).
            Given as a specified type OR list of a specified type.
            'all' can be used to select all marker collections.
            Comma-colon separated strings can be used to select marker collections in plotted order.
                e.g. '0' = '1st marker col', '0,1' = '1st, 2nd marker col', '1:3' = '2nd, 3rd, 4th marker col'
        legend_markers (bool): Sets properties for legend markers if True, otherwise sets properties for markers plotted
            on specified axis object.
    Returns:
        (dict): Marker properties for each marker collection specified (e.g. '0', '1', 'all') as a nested dictionary.
    """
    markers_master, markers_name = _get_master_objs(ax, 'marker collection', matplotlib.collections.PathCollection,
                                                    ax.collections, legend_markers)
    defaults = get_defaults()
    # Fix default properties to be consistent with matplotlib conventions
    _fix_props(defaults['marker_props'], markers_name)
    return _get_props(which_markers, markers_master, markers_name, defaults['marker_props'])


def set_marker_props(ax, which_markers, marker_props, legend_markers=False):
    """Set properties for markers.
    Args:
        ax (matplotlib.axes): Axis object.
        which_markers (int|str|matplotlib.collections.PathCollection): Marker collection/set index(es) or object(s).
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
    markers_master, markers_name = _get_master_objs(ax, 'marker collection', matplotlib.collections.PathCollection,
                                                    ax.collections, legend_markers)
    # Get appropriate marker object(s) from input as list
    which_markers = _get_plot_objects(which_markers, marker_props, markers_master, markers_name)
    if(which_markers):
        # Fix property input to be consistent with matplotlib conventions
        _fix_props(marker_props, markers_name)
        # Set properties using matplotlib.pyplot.setp
        _set_props(which_markers, markers_name, **marker_props)


def get_text_props(ax, which_texts, legend_texts=False):
    """Get properties of texts. The properties are returned in the order specified. If 'all' is given instead of an
    order then the text properties are returned in the default order: '0', '1', '2' etc.
    Args:
        ax (matplotlib.axes): Axis object.
        which_texts (int|str|matplotlib.text.Text): text index(es) or object(s).
            Given as a specified type OR list of a specified type.
            'all' can be used to select all texts.
            Comma-colon separated strings can be used to select texts in plotted order.
                e.g. '0' = '1st text', '0,1' = '1st, 2nd text', '1:3' = '2nd, 3rd, 4th text'
        legend_texts (bool): Sets properties for legend texts if True, otherwise sets properties for texts plotted on
            specified axis object.
    Returns:
        (dict): text properties for each text specified (e.g. '0', '1', 'all') as a nested dictionary.
    """
    texts_master, texts_name = _get_master_objs(ax, 'text', matplotlib.text.Text,
                                                    ax.texts, legend_texts)
    defaults = get_defaults()
    _fix_props(defaults['text_props'], texts_name)
    return _get_props(which_texts, texts_master, texts_name, defaults['text_props'])


def set_text_props(ax, which_texts, text_props, legend_texts=False):
    """Set properties for texts.
    Args:
        ax (matplotlib.axes): Axis object.
        which_texts (int|str|matplotlib.text.Text): Text index(es) or object(s).
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
    texts_master, texts_name = _get_master_objs(ax, 'text', matplotlib.text.Text,
                                                    ax.texts, legend_texts)
    # Get appropriate text object(s) from input as list
    which_texts = _get_plot_objects(which_texts, text_props, texts_master,
                                    texts_name)
    if(which_texts):
        if('fontname' in text_props):
            if(legend_texts):
                warnings.warn("Legend font can not be changed this way as it is rendered as mathtext. "
                              "Use set_font('font', mathtext=True) to set the mathtext font within the plot instead.")
            else:
                # Check if text contains mathtext and if so change the mathtext font to accommodate
                _change_mathtext(which_texts, text_props['fontname'])
        if('fontsize' in text_props and legend_texts):
            # More than one fontsize is not supported in legend text
            if(len(set(get_iterable(text_props['fontsize']))) > 1):
                warnings.warn("Only one fontsize can be used in legend text.")
        _fix_props(text_props, texts_name)
        # Set properties using matplotlib.pyplot.setp
        _set_props(which_texts, texts_name, **text_props)


def get_legend_props(ax, which_legends):
    """Get properties of legend. The legend properties are returned in the order specified. If 'all' is given instead
    of an order then the properties are returned in the default order: '0', '1', '2' etc.
    All additional legends added via plt.gca().add_artist are automatically processed by default, or can be specified
    using indexes >=1 (0 = native axis legend).
    Args:
        ax (matplotlib.axes): Axis object.
        which_legends (int|str|matplotlib.legend.Legend): Legend index(es) or object(s).
            Given as a specified type OR list of a specified type.
            'all' can be used to select all objects.
            Comma-colon separated strings can be used to select objects in plotted order.
                e.g. '0' = '1st legend', '0,1' = '1st, 2nd legend', '1:3' = '2nd, 3rd, 4th legend'
    Returns:
        (dict): text properties for each text specified (e.g. '0', '1', 'all') as a nested dictionary.
    """
    # Get master list of all legends in plot including additional legends added via add_artist
    legends_master = [ax.legend_]
    legends_master.extend([l for l in ax.artists if isinstance(l, matplotlib.legend.Legend)])

    which_legends = _get_plot_objects(which_legends, True, legends_master, 'legend')

    defaults = get_defaults()
    legend_props = _get_props(which_legends, legends_master, 'legend', defaults['legend_props'])
    # Convert bbox output into tuple (x0, y0, width, height) coords
    legend_props['bbox_to_anchor'] = [_bbox_to_coords(ax, bbox) for bbox in legend_props['bbox_to_anchor']]
    return legend_props


def set_legend_props(ax, which_legends, legend_props):
    """Set properties for legends.
    Args:
        ax (matplotlib.axes): Axis object.
        which_legends (int|str|matplotlib.legend.Legend): Legend index(es) or object(s).
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
            bbox_to_anchor (tuple|list): Coordinates to position legend: (x0, y0)
    Returns:
        None
    """
    # Get master list of all legends in plot including additional legends added via add_artist
    legends_master = [ax.legend_]
    legends_master.extend([l for l in ax.artists if isinstance(l, matplotlib.legend.Legend)])

    which_legends = _get_plot_objects(which_legends, legend_props, legends_master, 'legend')

    if(which_legends):
        _fix_props(legend_props, 'legend')
        # Position updated legend in same location as previous if bbox_to_anchor is not specified
        if('_bbox_to_anchor' not in legend_props):
            legend_props['_bbox_to_anchor'] = [wl.get_bbox_to_anchor() for wl in which_legends]
        # Otherwise convert (x0, y0, (width, height)) tuple|list into Bbox object
        else:
            legend_props['_bbox_to_anchor'] = _get_legend_bboxes(ax, legend_props['_bbox_to_anchor'])
        _set_props(which_legends, 'legend', redraw=False, **legend_props)
        # Update legend artists to reflect changes
        legend_artists = [wl for wl in which_legends]
        plt.gca().artists = list(set(plt.gca().artists) | set(legend_artists))


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


def set_log_scale(ax, which_axes, log_scale_props):
    """
    Args:
        ax (matplotlib.axes): Axis object.
        which_axes (int|str|matplotlib.axis.(XAxis|YAxis)): Axes index(es) or object(s).
            Given as a specified type OR list of a specified type.
            Names accepted are 'x' or 'y', or 'all' can be used to select both axes.
            Comma-colon separated strings can be used to select axes in 'x', 'y' order.
                e.g. '0' = 'x', '0,1' = 'x, y'
        log_scale_props (dict): Scale properties. Call get_available_scales() or see matplotlib.scale documentation
            for full properties list. Note, however, that in contrast to matplotlib implementation, keyword args
            should not have axis name suffix (e.g. 'basex' is just 'base' and which_axes determines the 'base' type).
            scale (str): 'log', 'linear', 'symlog' or 'logit'.
            base (int): Logarithmic base. Only used if scale='log'.
            nonpos (str): Whether to "mask" or "clip" non positive values if scale='log'
                or values near 0 and 1 in scale='logit'.
            subs (list): List of integer spacings for minor ticks.
            linscale (float): Stretching of linear range "linthresh" relative to log range if scale='symlog'.
            exponents (bool): Whether to change ticklabels into exponents.
            exponents_precision (int): Precision with which to display exponent ticklabels.
            hide_base (bool): Whether to hide base in label text.
            base_precision (int): Precision with which to display base in label text.
    Returns:
        None
    """
    # Get appropriate axis/axes objects from input as list
    which_axes = _get_plot_objects(which_axes, log_scale_props, {'x': ax.xaxis, 'y': ax.yaxis},
                                   'axis', ['x', 'y'])
    # Store parameters separately as iterables as they aren't keyword arguments in matplotlib set_(x/y)scale
    scale = map_list(get_iterable(log_scale_props.pop('scale', None)), len(which_axes))
    exponents = map_list(get_iterable(log_scale_props.pop('exponents', None)), len(which_axes))
    exponents_precision = map_list(get_iterable(log_scale_props.pop('exponents_precision', 2)),
                                         len(which_axes))
    hide_base = map_list(get_iterable(log_scale_props.pop('hide_base', False)), len(which_axes))
    base_precision = map_list(get_iterable(log_scale_props.pop('base_precision', 0)), len(which_axes))

    # Convert property values into iterables with same length as number of axes
    log_scale_props = {k: map_list(get_iterable(v), len(which_axes)) for k, v in log_scale_props.items()}
    for i, (wa, s, exp, exp_prec, hb, bp) in \
            enumerate(zip(which_axes, scale, exponents, exponents_precision, hide_base, base_precision)):
        axis_name = wa.axis_name
        scale_dict = {}
        for k, v in log_scale_props.items():
            scale_dict[k+axis_name] = v[i]
        if(axis_name == 'x'):
            ax.set_xscale(wa.get_scale() if s is None else s, **scale_dict)
        elif(axis_name == 'y'):
            ax.set_yscale(wa.get_scale() if s is None else s, **scale_dict)
        if(exp):
            try:
                base = wa._scale.base  # This allows user to set exponent properties without needing to specify the base
            except AttributeError:
                raise AttributeError("Can not access private variable '_scale.base'. Matplotlib may have been updated "
                                     "and changed this variable. Getting base value this way is no longer possible.")
            else:
                _set_axis_exponent(wa, base, exp_prec, hb, bp)


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
        # font.family is converted to list in built-in matplotlib function so here we flatten it back to string
        return matplotlib.rcParams['font.family'][0]


def set_font(font, mathtext=False):
    """Get font on system and set plot font (normal or mathtext).
    Args:
        font: Font name.
        mathtext (bool): Sets mathtext rather than normal plot text if True.
    Returns:
        None
    """
    font = _get_system_font(font)
    if(font):
        _set_font(font, mathtext)


def get_mathtext():
    """Get plot mathtext via get_font(mathtext=True)
    Returns:
        (str): matplotlib.rcParams font parameter.
    """
    return get_font(True)


# MISCELLANEOUS GETTER FUNCTIONS ------------------------------------------------


@conditional_decorator(sys.version_info.major == 3, 'lru_cache', decorator_args=2, module=functools)
def get_defaults(file="defaults.json"):
    """Load default pyblish plot parameters.
    Args:
        file (str): File where defaults are stored in json format.
    Returns:
        data (dict): Default parameters.
    """
    with open(file, 'r') as fp:
        data = json.load(fp)
    return data


@conditional_decorator(sys.version_info.major == 3, 'lru_cache', decorator_args=2, module=functools)
def get_available_fonts():
    """Use matplotlib.font_manager to get fonts on system.
    Returns:
         Alphabetically sorted list of .ttf font names.
    """
    fmanager = fm.FontManager()
    font_names = set([f.name for f in fmanager.ttflist])
    return sorted(font_names)


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


def _get_system_font(font):
    """Get name of font on system by taking the closest match between font specified and fonts on system.
    Args:
        font (str): Font name.
    Returns:
        (str): Font name as it is defined on system.
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
            warnings.warn("'{}' font not found and therefore not changed. Use get_available_fonts() or print_"
                          "available_fonts() to see fonts installed on this system.".format(font))
            return None


def _get_plot_properties(which_props, user_defined, defaults):
    """Override default plot properties with user-specified key: value pairs.
    Args:
        which_props (list): List of properties to process.
        user_defined (dict): User-defined properties to use for overriding.
        defaults (dict): Default properties that are returned if no user-specified properties given.
    Returns:
        plot_props (dict): Dictionary of plotting properties.
    """
    plot_props = {}
    for wp in which_props:
        plot_props[wp] = defaults[wp]
        props = user_defined.get(wp, None)
        if(props):
            for k in plot_props[wp].keys():
                if(k in props):
                    plot_props[wp][k] = props[k]
    return plot_props


def _get_plot_objects(objs, objs_props, objs_master, objs_name, objs_keys=None):
    """Get plotted objects from parsed input.
    Args:
        objs (int|str|matplotlib objects): Object index(es) or object(s).
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
    if(all([om is None for om in objs_master])):
        raise InputError("Trying to set {0} properties but no {0} objects were found.".format(objs_name))
    else:
        if(objs_keys):
            # Convert master object dictionary to list in same order as keys specified
            objs_master = [objs_master[k] for k in get_iterable(objs_keys)]

    # Check if properties have been set
    if(objs_props is None):
        raise InputError("Trying to access {0} objects but no {0} properties were specified.".format(objs_name))
    if(objs is None):
        raise InputError("Trying to access {0} objects but no {0}s were found.".format(objs_name))
    elif(objs == 'all'):
        objs = objs_master  # Set objects to master list (i.e. all objects)
    # Parse input and add appropriate plot objects to list
    objs_return = []

    assert objs_keys is None or isinstance(objs_keys, list)

    # Convert object and master list to iterables
    objs = get_iterable(objs)

    for wo in objs:
        if(isinstance(wo, int)):
            objs_return.append(objs_master[wo])
        elif(isinstance(wo, str)):
            # If input is all numbers and '-'/':'/',' then parse input into index ranges
            wo = wo.replace(' ', '')
            if(all([(c.isdigit() or c in [':', '-', ',']) for c in wo])):
                try:
                    indexes = parse_str_ranges(wo)
                    for i in indexes:
                        try:
                            objs_return.append(objs_master[i])
                        except IndexError:
                            raise InputError("Input index '{}' exceeds {} list with length of {}."
                                             .format(i, objs_name, len(objs_master)))
                except ValueError as e:
                    raise InputError("{}".format(str(e)))
            # Otherwise use input as key in master list
            else:
                try:
                    objs_return.append(objs_master[objs_keys.index(wo)])
                except ValueError:
                    raise InputError("Only '{}' and 'all' are accepted object name inputs."
                                     .format("', '".join(objs_keys)))
        elif(isinstance(wo, tuple([type(om) for om in objs_master]))):
            objs_return.append(wo)
        else:
            raise InputError("Unrecognised object '{}'".format(wo))

    return objs_return


def _get_master_objs(ax, objs_name, objs_type, default_master, legend_objs=False):
    if(legend_objs):
        try:
            if(objs_name == 'text'):
                # Get legend texts
                objs_master = ax.legend_.texts
            else:
                # Get appropriate lines or markers from legend handles
                objs_master = [h for h in ax.legend_.legendHandles if isinstance(h, objs_type)]
            objs_name = "legend {}".format(objs_name)
        except AttributeError:
            raise AttributeError("Trying to get legend {} properties but no legend was found.".format(objs_name))
    else:
        # Get plot objects
        objs_master = default_master
        objs_name = "{}".format(objs_name)

    if(objs_master):
        return objs_master, objs_name
    else:
        raise InputError("Trying to get {0} properties but no {0} objects were found.".format(objs_name))


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
            _get_marker_paths(s, False)
        else:
            # Convert string into marker object
            m = matplotlib.markers.MarkerStyle(s)
            # Convert marker object to path object and transform to figure coordinates
            if(top_level):
                # Convert to list if this is the list top level as each input to markers set_paths() must be list or
                # tuple
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
    if(coords):
        if(isinstance(coords, tuple)):
            coords = _coords_to_bbox(ax, coords)
        elif(isinstance(coords, list)):
            for i, c in enumerate(coords):
                coords[i] = _get_legend_bboxes(ax, c)
        elif(isinstance(coords, matplotlib.transforms.TransformedBbox)):
            pass
        else:
            raise InputError("Unrecognised value for bbox_to_anchor. Valid inputs are bbox objects, tuples, or list of "
                             "tuples|bbox objects.")
    else:
        coords = None

    return coords


def _get_props(objs, objs_master, objs_name, objs_attrs, objs_keys=None, get_ticks=None):
    """Get plotted object properties.
    Args:
        objs (int|str|matplotlib objects): Object index(es) or object(s).
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
    objs_props = {}
    # Iterate through object attributes and add to property dictionary using built in getter functions for matplotlib
    # object and user-friendly attribute names
    for k in objs_attrs:
        if(get_ticks):
            objs_props[k] = [_get_tick_props(wo, get_ticks).get(k) for wo in objs]
        else:
            objs_props[k] = [plt.getp(wo, k) for wo in objs]
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
        else:
            raise InputError("Tick type must be 'minor' or 'major'.")
    except AttributeError as e:
        raise AttributeError("Can not access private variable '_major_tick_kw'. Matplotlib may have been updated and "
                             "changed this variable. Getting major tick properties is no longer possible."
                             .format(re.findall("'_.+'", e.args[0])[-1]))
    else:
        return tick_props


# PRIVATE SETTER FUNCTIONS --------------------------------------------------------------------------------------------


def _set_master_defaults(defaults):
    """Set default parameters that = 'master' to appropriate master default value.
    e.g. linewidth, linestyle, fontname, fontsize
    Args:
        defaults (dict): Default plot properties read from defaults file.
    Returns:
         defaults (dict): Updated default properties with 'default' values replaced by master values.
    """
    for k, kv in defaults.items():
        if(isinstance(kv, dict)):
            for kk, kkv in kv.items():
                if(kkv == 'master'):
                    defaults[k][kk] = defaults['master_defaults'][kk]
                # bbox_to_anchor has to be given as a list in defaults file but must be a tuple for matplotlib
                if(kk == 'bbox_to_anchor'):
                    defaults[k][kk] = None if defaults[k][kk] == 'None' else tuple(defaults[k][kk])
        else:
            if(kv == 'master'):
                defaults[k] = defaults['master_defaults'][k]
    return defaults


def _set_params_defaults(defaults, num_cols):
    """Set default values for parameters that are dependent on the number of figure-spanning columns requested.
    Args:
        defaults (dict): Dictionary of default plotting parameters that supports dot notation.
        num_cols (int): Number of columns the figure will span in article.
    Returns:
        defaults (dict): Dictionary of updated default plotting parameters that supports dot notation.

    """
    defaults['spine_props']['linewidth'] = \
        _add_to_parameter(defaults['spine_props']['linewidth'], (num_cols - 1) * 1)
    defaults['label_props']['fontsize'] = \
        _add_to_parameter(defaults['label_props']['fontsize'], (num_cols - 1) * 6)
    defaults['major_tick_props']['labelsize'] = \
        _add_to_parameter(defaults['major_tick_props']['labelsize'], (num_cols - 1) * 4)
    defaults['major_tick_props']['width'] = \
        _add_to_parameter(defaults['major_tick_props']['width'], (num_cols - 1) * 1)
    defaults['minor_tick_props']['labelsize'] = \
        _add_to_parameter(defaults['minor_tick_props']['labelsize'], (num_cols - 1) * 4)
    defaults['minor_tick_props']['width'] = \
        _add_to_parameter(defaults['minor_tick_props']['width'], (num_cols - 1) * 1)
    defaults['line_props']['linewidth'] = \
        _add_to_parameter(defaults['line_props']['linewidth'], (num_cols - 1) * 1)
    defaults['marker_props']['sizes'] = \
        _add_to_parameter(defaults['marker_props']['sizes'], (num_cols - 1) * 50)
    defaults['text_props']['fontsize'] = \
        _add_to_parameter(defaults['text_props']['fontsize'], (num_cols - 1) * 4)
    defaults['legend_line_props']['linewidth'] = \
        _add_to_parameter(defaults['legend_line_props']['linewidth'], (num_cols - 1) * 1)
    defaults['legend_marker_props']['sizes'] = \
        _add_to_parameter(defaults['legend_marker_props']['sizes'], (num_cols - 1) * 50)
    defaults['legend_text_props']['fontsize'] = \
        _add_to_parameter(defaults['legend_text_props']['fontsize'], (num_cols - 1) * 4)

    return defaults


def _set_rcparams_defaults(defaults_dict):
    """Set default matplotlib.rcParams that define how the figure is rendered.
    Args:
        defaults_dict (dict): Dictionary of default plotting parameters.
    Returns:
        None
    """
    rc_params = matplotlib.rcParams
    rc_params['axes.unicode_minus'] = defaults_dict['use_unicode_minus']  # use smaller minus sign in plots
    rc_params['axes.formatter.use_mathtext'] = defaults_dict['use_mathtext']  # use mathtext for scientific notation
    rc_params['figure.dpi'] = defaults_dict['dpi']
    rc_params['savefig.dpi'] = defaults_dict['dpi']


def _set_font(font, mathtext=False):
    """Set plot font (normal or mathtext). This function assumes the font is defined on the system.
    The method for setting mathtext is experimental and may be removed in future updates to matplotlib.
    Args:
        font: Font name.
        mathtext (bool): Sets mathtext rather than normal plot text if True.
    Returns:
        None
    """
    assert font in get_available_fonts() + ['stixsans', 'cm', 'sans']
    if(mathtext):
        # Check if font is one of the 3 global fontsets
        if(font in ['cm', 'sans', 'stixsans']):
            matplotlib.rcParams['mathtext.fontset'] = font
        else:
            matplotlib.rcParams['mathtext.fontset'] = 'custom'
            matplotlib.rcParams['mathtext.cal'] = font
            matplotlib.rcParams['mathtext.rm'] = font
            matplotlib.rcParams['mathtext.bf'] = font
            matplotlib.rcParams['mathtext.it'] = font
            matplotlib.rcParams['mathtext.tt'] = font
            matplotlib.rcParams['mathtext.sf'] = font
    else:
        matplotlib.rcParams['font.family'] = font


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


def _set_axis_exponent(ax, base, precision, hide_base, base_precision=0):
    """Set tick labels to log_base of values, which is the exponent of the mantissa (e.g. 10^2 -> 2 in log base 10)
    and add log_base to axis label text if it doesn't exist.
    Args:
        ax (matplotlib.axes): Axis object.
        base (int): Logarithmic base.
        precision (int): Floating point precision for exponent values.
        hide_base (bool): Whether to hide base in label text
    Returns:
        None
    """
    if('log' in ax.get_scale()):
        try:
            ax.set_major_formatter(FuncFormatter(lambda x, p: "{1:.{0}f}"
                                                 .format(precision, math.log(x, base))))
        except ValueError:
            raise ValueError("Ticks can not be <= 0 if using a logarithmic scale. Use scale='symlog' instead.")
        else:
            _add_label_log(ax, base, hide_base, base_precision)  # Add 'log' to label text if necessary
    else:
        warnings.warn("'{}' axis scale is '{}' so ignoring logarithmic exponent formatting."
                      .format(ax.axis_name, ax.get_scale()))


def _set_props(objs, objs_name, set_ticks=None, redraw=True, **kwargs):
    """Set plotted object properties.
    Args:
        objs (list): Object(s) to apply property changes to.
        objs_name (str): Name of object type.
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
    kwargs = remove_empty_keys(kwargs)
    kwargs = {k: map_list(get_iterable(v), len(objs)) for k, v in kwargs.items()}
    for i, o in enumerate(objs):
        props_dict = {}
        for k, v in kwargs.items():
            # If the property can be changed and the canvas redrawn then populate dictionary with property values
            if(redraw):
                props_dict[k] = v[i]
            # Otherwise set values manually for each property to avoid redrawing canvas (for legend)
            else:
                try:
                    setattr(o, k, v[i])
                except (TypeError, ValueError):
                    raise InputError("Could not set {} properties.".format(objs_name))
        if(props_dict):
            if(set_ticks):
                try:
                    o.set_tick_params(set_ticks, **props_dict)
                except (TypeError, ValueError):
                    raise InputError("Could not set {} properties.".format(objs_name))
            else:
                try:
                    plt.setp(o, **props_dict)
                except (TypeError, ValueError):
                    raise InputError("Could not set {} properties.".format(objs_name))


# PRIVATE MISCELLANEOUS FUNCTIONS ---------------------------------------


def _fix_defaults(defaults):

    _fix_props(defaults['spine_props'], 'spine')
    _fix_props(defaults['major_tick_props'], 'ticks')
    _fix_props(defaults['minor_tick_props'], 'ticks')
    _fix_props(defaults['label_props'], 'label')
    _fix_props(defaults['line_props'], 'line')
    _fix_props(defaults['legend_line_props'], 'legend line')
    _fix_props(defaults['marker_props'], 'line')
    _fix_props(defaults['legend_marker_props'], 'legend marker')
    _fix_props(defaults['text_props'], 'text')
    _fix_props(defaults['legend_text_props'], 'legend text')
    _fix_props(defaults['legend_props'], 'legend')


def _fix_props(props, prop_name):
    if(prop_name == 'spine'):
        if('linecolor' in props):
            props['edgecolor'] = props.pop('linecolor')
    elif(prop_name == 'ticks'):
        if('fontsize' in props):
            props['labelsize'] = props.pop('fontsize')
        if('fontcolor' in props):
            props['labelcolor'] = props.pop('fontcolor')
    elif(prop_name == 'label'):
        if('fontcolor' in props):
            props['color'] = props.pop('fontcolor')
    elif('line' in prop_name):
        if('linecolor' in props):
            props['color'] = props.pop('linecolor')
    elif('marker' in prop_name):
        if('linecolor' in props):
            props['edgecolor'] = props.pop('linecolor')
        if('sizes' in props):
            # Convert any non-iterable size value to an iterable as this is the input for the built-in matplotlib
            # function
            props['sizes'] = [_ if isinstance(_, list) else [_] for _ in get_iterable(props['sizes'])]
        if('symbols' in props):
            # Convert symbol strings to path objects
            props['paths'] = _get_marker_paths(get_iterable(props.pop('symbols')))
    elif('text' in prop_name):
        if('fontname' in props and 'legend' in prop_name):
            # Get closest matching font or None if font not found
            props['fontname'] = _get_system_font(props['fontname'])
        if('fontcolor' in props):
            props['color'] = props.pop('fontcolor')
    elif(prop_name == 'legend'):
        # Update legend attribute names to those used for matplotlib legend object
        for n, k in zip(['bbox_to_anchor', 'loc', 'ncol', 'frameon'],
                        ['_bbox_to_anchor', '_loc', '_ncol', '_drawFrame']):
            if(n in props):
                props[k] = props.pop(n)


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


def _add_to_parameter(list_in, addition):
    """Convert parameter to an iterable and add to each element by the same amount.
    Args:
        list_in (int|list): Value or list to add to.
        addition (float): Value to add to each list element.
    Returns:
        (list): Array with each element incremented by addition.
    """
    try:
        return [_ + addition for _ in get_iterable(list_in)]
    except ValueError:
        ValueError("Could not add {} to each element of list {}".format(addition, list_in))


def _change_mathtext(texts, font):
    if(texts):
        for text in texts:
            t = text.get_text()
            if(re.match('(.+)?(\$.+\$)(.+)?', t)):
                if not(font == get_mathtext()):
                    warnings.warn("Text '{}' contains mathtext that can not have font changed individually. "
                                  "Therefore the mathtext in the entire plot has been changed to {}."
                                  "If this is not the desired outcome then either set the mathtext back to the default"
                                  "or remove the mathtext and re-run.".format(t, font))
                    _set_font(font, mathtext=True)


def _add_label_log(ax, base, hide_base, base_precision):
    """Add log_base to axis label text if it doesn't exist.
    Args:
        ax (matplotlib.axes): Axis object.
        base: Logarithmic base.
    Returns:
        None
    """
    # Add 'log_base' to axis label if doesn't already start with 'log'
    label_stripped = re.sub(r'(\$)(\\?\w+\{)+', '', ax.get_label_text())
    if(label_stripped.startswith('log')):
        if(base != 10.0 and not label_stripped.startswith('log_{1:.{0}f}'.format(base_precision, base))):
            warnings.warn("Label text has a log identifier but without the requested base indicated. Either add the "
                          "base suffix in the mathtext or remove the log and it will be added with the correct base "
                          "automatically.")
    else:
        if(hide_base):
            base_part = ''
        else:
            base_part = '{:.{}f}'.format(base, base_precision)
        ax.set_label_text('$\mathrm{' + 'log_{%s}' % (base_part) + '}$ ' + ax.get_label_text())


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


# PRINT FUNCTIONS --------------------------------------------------------------------------------------------------


def print_linestyles():
    print(get_available_linestyles())


def print_axes_scales(keywords=False):
    print(get_available_scales(keywords))


def print_legend_locs():
    print(get_available_legend_locs())


def print_fonts():
    print('\n'.join(get_available_fonts()))
