#!/usr/bin/python

#from __future__ import print_function

import warnings
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import json
import re

from utils import utils

# ToDo: Main

# make set_legend_props select between lines, marker and texts more intelligently
# make get functions to accompany set functions
# make docstrings user-friendly - done main functions

# set custom colour cycle for lines to nice sequence - use ColorMapper module from laptop!


class DotDict(dict):
    '''
    Dictionary object with dot notation access
    '''
    def __getattr__(self, attr):
        return self.get(attr)
    __setattr__= dict.__setitem__
    __delattr__= dict.__delitem__


def pyblishify(fig, num_cols, aspect='square', which_labels='both', which_ticks='both',
                   which_spines=('left', 'bottom'),
                   which_lines='all', which_markers='all', which_texts='all',
                   which_legend_handles='all', which_legend_labels='all',
                   change_log_scales=True):

    # Convert dictionary to DotDict which is a dict wrapper that allows dot notation
    defaults_dict = DotDict(_load_defaults())
    # Set defaults that are dependent on number of columns requested
    defaults_dict = _set_params_defaults(defaults_dict, num_cols)
    # Override a selection of default rcParams
    _set_rcparams_defaults(defaults_dict)
    # Set mathtext font
    set_mathtext_font(defaults_dict.default_mathtext)

    # Convert aspect variable to number
    aspect_val = _get_aspect_val(aspect)
    # Set figure size
    fig_width, fig_height = _get_figure_size(num_cols, aspect_val)
    set_figure_size(fig, fig_width, fig_height)

    # Apply changes to all axis objects in figure
    for ax in fig.axes:

        # Set axes label properties using default label properties
        if(which_labels is not None):
            set_label_props(ax, 'all',
                            label_props=dict(fontsize=defaults_dict.label_size*3, fontname=None, color=None))

        # Set axes ticks and ticklabel properties using default tick and ticklabel properties
        if(which_ticks is not None):
            set_tick_props(ax, 'all',
                           tick_props=dict(size=defaults_dict.majortick_size, width=defaults_dict.line_width, color='green',
                                           direction=defaults_dict.tick_dir, pad=defaults_dict.ticklabel_pad,
                                           labelsize=defaults_dict.ticklabel_size, labelcolor='purple'),
                           tick_type='major')
            set_tick_props(ax, 'all',
                           tick_props=dict(size=defaults_dict.minortick_size, width=defaults_dict.line_width, color='blue',
                                           direction=defaults_dict.tick_dir, pad=defaults_dict.ticklabel_pad,
                                           labelsize=defaults_dict.ticklabel_size, labelcolor='red'),
                           tick_type='minor')

        # Set axes log scale properties
        if(change_log_scales):
            set_log_exponents(ax, 'all')
        # Set axes spine properties using default spine properties
        if(which_spines is not None):
            set_spine_props(ax, 'all',
                            spine_props=dict(
                                             linewidth=defaults_dict.spine_width,
                                             edgecolor=['blue', 'red']))
        # Set line properties using default line properties
        if(which_lines is not None):
            if(ax.lines):
                set_line_props(ax, [0,1],
                               line_props=dict(
                                               linewidth=defaults_dict.line_width*2,
                                               color=defaults_dict.col_cycle,
                                               linestyle='-'))
        # Set marker properties using default marker properties
        if(which_markers is not None):
            if(ax.collections):
                set_marker_props(ax, '1',
                                      marker_props=dict(
                                              sizes=100,#defaults_dict.marker_size,
                                              linewidth=defaults_dict.line_width,
                                              linestyle=[['-', ':']],
                                              facecolor=[defaults_dict.col_cycle],
                                              edgecolor=[defaults_dict.col_cycle],
                                             symbols='o'))
        # Set text properties using default text properties
        if(which_texts is not None):
            set_text_props(ax, 'all',
                                text_props=dict(
                                        fontsize=defaults_dict.texts_size,
                                        color='green',
                                        fontname='Arial'))
        # Set legend properties using old legend properties and new lines and markers properties
        if(ax.get_legend() and (ax.lines or ax.collections)):
            set_legend_props(ax, 'all', 'all', '0:1',
                             text_props={'color': 'blue'}
                             )


def set_figure_size(fig, fig_width, fig_height):
    '''
    Set figure size
    :param fig: [matplotlib.figure.Figure]
    :param fig_width: [float]
    :param fig_height: [float]
    :return: None
    '''
    _set_figure_size(fig, fig_width, fig_height)


def set_mathtext_font(font):
    '''
    Set mathtext font which defines how text within $$ will look. Some custom fonts may not work correctly.
    :param font: [str] Font name
    :return: None
    '''
    if(font in ['stixsans', 'stix', 'cm']):
        matplotlib.rcParams['mathtext.fontset'] = font
    else:
        matplotlib.rcParams['mathtext.fontset'] = 'custom'
        matplotlib.rcParams['mathtext.rm'] = font
        matplotlib.rcParams['mathtext.it'] = '%s:italic' % font
        matplotlib.rcParams['mathtext.bf'] = '%s:bold' % font


def set_spine_props(ax, which_spines, spine_props, hide_other_spines=True, duplicate_ticks=False):
    """Set properties for spines.

    Args:
        ax (matplotlib.axes): Axis object.
        which_spines (int|str|matplotlib.spines.Spine): spine index(es) as integers, names or objects.
            Given as a specified type OR list of a specified type.
            Names accepted are 'left', 'bottom', 'right', 'top', or 'all' can be used to select all spines.
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
    spines = ax.spines
    spines_dict = {'left': ax.yaxis, 'bottom': ax.xaxis, 'right': ax.yaxis, 'top': ax.xaxis}
    # Get appropriate spine object(s) from input
    which_spines = _get_plot_elements(ax, which_spines, ax.spines,
                                      'spine', matplotlib.spines.Spine,
                                      ['left', 'bottom', 'right', 'top'])
    # Get list of spines unspecified which will be made invisible
    which_spines_invis = [v for k,v in spines.items() if v not in which_spines]

    # Turn off all spines and ticks and labels initially
    for ax_label, ax_dir in spines_dict.items():
        ax_dir.set_tick_params(which='both', **{ax_label: 'off'}, **{'label'+ax_label: 'off'})
    # Turn on requested spines and ticks and labels
    for sp in which_spines:
        ax_label = list(ax.spines.keys())[list(spines.values()).index(sp)]
        ax_dir = spines_dict[ax_label]
        ax_dir.set_tick_params(which='both', **{ax_label: 'on'}, **{'label'+ax_label: 'on'})
        # Avoid duplication of ticks on both sides of plot if requested
        if not(duplicate_ticks):
            ax_dir.set_ticks_position(ax_label)

    if(spine_props and which_spines):
        _set_props(ax, which_spines, **spine_props)
        # Hide unspecified spines
        if(hide_other_spines):
            _set_props(ax, which_spines_invis, visible=False)
    else:
        warnings.warn("Trying to set spine properties but no spines were specififed.")


def set_tick_props(ax, which_axes, tick_props, tick_type='major'):
    """Set properties for axes ticks

    Args:
        ax (matplotlib.axes): Axis object.
        which_axes (int|str|matplotlib.axis.(XAxis|YAxis)) axes indexes as integers, names or objects.
            Given as a specified type OR list of a specified type.
            Names accepted are 'x' or 'y', or 'both' can be used to select both axes.
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
    # Get appropriate axis/axes objects from input
    axes_dict = {'x': ax.xaxis, 'y': ax.yaxis}
    which_axes = _get_plot_elements(ax, which_axes, axes_dict,
                                    'tick',
                                    (matplotlib.axis.XAxis, matplotlib.axis.YAxis),
                                    axes_dict.keys())
    # Set tick properties
    if(tick_props and which_axes):
        tick_props = utils.remove_empty_keys(tick_props)
        for wa in which_axes:
            wa.set_tick_params(tick_type, **tick_props)
    else:
        warnings.warn("Trying to set tick properties but no axes were specified.")


def set_label_props(ax, which_labels, label_props):
    """Set properties for axes labels

    Args:
        ax (matplotlib.axes): Axis object.
        which_axes (int|str|matplotlib.axis.(XAxis|YAxis)) axes indexes as integers, names or objects.
            Given as a specified type OR list of a specified type.
            Names accepted are 'x' or 'y', or 'both' can be used to select both axes.
        label_props (dict): Label properties. Each property can be given as an appropriate type and applied to all labels.
            Alternatively, a list may be given for each property so that each label is assigned different properties.
                fontsize (float): Label font size(s)
                fontname (str): Label font(s)
                color (str|tuple): Label color(s) as hex string(s) or RGB tuple(s)

    Returns:
        None
    """
    # Check if there's mathtext if user requests a custom font as it will change font for
    # all mathtext in the plot
    if('fontname' in label_props):
        _check_mathtext(ax, label_props['fontname'])
    # Get appropriate axis label(s) objects from input
    labels_dict = {'x': ax.xaxis.label, 'y': ax.yaxis.label}
    which_labels = _get_plot_elements(ax, which_labels, labels_dict,
                                    'label', matplotlib.text.Text,
                                      labels_dict.keys())
    # Set label properties
    if(label_props and which_labels):
        _set_props(ax, which_labels, **label_props)
    else:
        warnings.warn("Trying to set label properties but no axes were specified.")


def set_line_props(ax, which_lines, line_props, **kwargs):
    """Set properties for lines

    Args:
        ax (matplotlib.axes): Axis object.
        which_lines (int|str|matplotlib.lines.Line2D) line index(es) as integers or objects.
            Given as a specified type OR list of a specified type.
            'all' can be used to select all lines.
        line_props (dict): Line properties. Each property can be given as an appropriate type and applied to all lines.
            Alternatively, a list may be given for each property so that each line is assigned different properties.
                linewidth (int|float): Line width(s)
                color (str|tuple): Line color(s) as hex string(s) or RGB tuple(s)
                linestyle (str): Line style(s): '-', '--', ':'
        **kwargs: Semi-hidden parameters the typical user does not need to worry about, which are used to
            distinguish between plotted lines and legend lines.
                lines_master (matplotlib.lines.Line2D): Line objects to target (defaults to ax.lines)
                lines_name (str): Name of lines to be passed to error message

    Returns:
        None
    """
    lines_master = kwargs.get('lines_master', ax.lines)
    lines_name = kwargs.get('lines_name', 'line')
    # Get appropriate line object(s) from input
    which_lines = _get_plot_elements(ax, which_lines, lines_master,
                                     lines_name,
                                     matplotlib.lines.Line2D)
    # Set line properties
    if(line_props and which_lines):
        _set_props(ax, which_lines, **line_props)
    else:
        warnings.warn("Trying to set line properties but no lines were specified.")


def set_marker_props(ax, which_markers, marker_props, **kwargs):
    """Set properties for markers

    Args:
        ax (matplotlib.axes): Axis object.
        which_markers (int|str|matplotlib.collections.PathCollection) marker collection/set index(es) as integers or
            objects.
            Given as a specified type OR list of a specified type.
            'all' can be used to select all marker collections.
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
        **kwargs: Semi-hidden parameters the typical user does not need to worry about, which are used to
            distinguish between plotted lines and legend lines.
                markers_master (matplotlib.collections.PathCollection): Marker collection objects to target
                    (defaults to ax.collections)
                markers_name (str): Name of markers to be passed to error message

    Returns:
        None
    """
    markers_master = kwargs.get('markers_master', ax.collections)
    markers_name = kwargs.get('markers_name', 'marker collection')
    # Get appropriate marker object(s) from input
    which_markers = _get_plot_elements(ax, which_markers, markers_master,
                                       markers_name,
                                       matplotlib.collections.PathCollection)

    # Convert sizes input to a nested list as this is the input for each collection in set_sizes()
    # This means incidentally that individual marker sizes can be set within each collection
    if('sizes' in marker_props):
        if(type(marker_props['sizes']) is not list or not any([isinstance(i, list) for i in marker_props['sizes']])):
            marker_props['sizes'] = [[s] for s in utils.get_iterable(marker_props['sizes'])]

    if('symbols' in marker_props):
        marker_props['paths'] = _get_marker_paths(utils.get_iterable(marker_props['symbols']))
        marker_props.pop('symbols')  # Remove symbols key as it is now paths
    # Set marker properties
    if(marker_props and which_markers):
        _set_props(ax, which_markers, **marker_props)
    else:
        warnings.warn("Trying to set marker properties but no markers were specified.")


def set_text_props(ax, which_texts, text_props, **kwargs):
    """Set properties for texts

    Args:
        ax (matplotlib.axes): Axis object.
        which_texts (int|str|matplotlib.text.Text) text index(es) as integers or objects.
            Given as a specified type OR list of a specified type.
            'all' can be used to select all texts.
        text_props (dict): Text properties. Each property can be given as an appropriate type and applied to all lines.
            Alternatively, a list may be given for each property so that each text is assigned different properties.
                fontsize (int|float): Text font size(s)
                color (str|tuple): Text font color(s) as hex string(s) or RGB tuple(s)
                fontname (str): Text font(s)
        **kwargs: Semi-hidden parameters the typical user does not need to worry about, which are used to
            distinguish between plotted texts and legend texts.
                texts_master (matplotlib.text.Text): Text objects to target (defaults to ax.texts)
                texts_name (str): Name of texts to be passed to error message

    Returns:
        None
    """
    texts_master = kwargs.get('texts_master', ax.texts)
    texts_name = kwargs.get('texts_name', 'text')
    # Get appropriate text object(s) from input
    which_texts = _get_plot_elements(ax, which_texts, texts_master,
                                     texts_name,
                                     matplotlib.text.Text)

    # Set text properties
    if(text_props and which_texts):
        _set_props(ax, which_texts, **text_props)
    else:
        warnings.warn("Trying to set text properties but no texts were specified.")


def set_legend_props(ax, which_lines=None, which_markers=None, which_texts=None,
                        line_props=None, marker_props=None, text_props=None,
                        frame_props=None):
    '''Set properties for legend lines, markers, texts and/or frame. Changes to plotted lines and markers before this
    function call are reflected in the legend lines/symbols automatically.
    Args:
        ax (matplotlib.axes): Axis object.
        which_lines (int|str|matplotlib.lines.Line2D) line index(es) as integers or objects.
            Given as a specified type OR list of a specified type.
            'all' can be used to select all lines.
        which_markers (int|str|matplotlib.collections.PathCollection) marker collection/set index(es) as integers or
            objects.
            Given as a specified type OR list of a specified type.
            'all' can be used to select all marker collections.
        which_texts (int|str|matplotlib.text.Text) text index(es) as integers or objects.
            Given as a specified type OR list of a specified type.
            'all' can be used to select all texts.
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
        legend_props (dict): Legend frame properties. See matplotlib.legend documentation for full properties list.
            loc (int):
            ncol (int): Number of columns
            frameon (bool): Frame border is visible if True
            columnspacing (float): Spacing between columns
            labelspacing (float): Spacing between symbols and text labels
            handlelength (float): Length of handles (only applicable for lines)
            numpoints (float): Number of symbols (only applicable for markers used on a line plot)
            scatterpoints (int): Number of symbols (only applicable on a scatter plot)
            bbox_to_anchor (tuple|list): Coords to position legend: (x0, y0)
    '''

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

    # Get appropriate lines and markers from new legend handles
    lines_master = [h for h in ax.legend_.legendHandles if isinstance(h, matplotlib.lines.Line2D)]
    markers_master = [h for h in ax.legend_.legendHandles if isinstance(h, matplotlib.collections.PathCollection)]

    # Set legend line properties
    if(line_props and which_lines):
        set_line_props(ax, which_lines, line_props,
                       lines_master=lines_master, texts_name='legend line')
    else:
        warnings.warn("Trying to set legend line properties but no legend lines were specified.")
    # Set legend marker properties
    if(marker_props and which_markers):
        set_marker_props(ax, which_markers, marker_props,
                         markers_master=markers_master, texts_name='legend marker collection')
    else:
        warnings.warn("Trying to set legend marker properties but no legend markers were specified.")
    # Set legend text properties
    if(text_props and which_texts):
        set_text_props(ax, which_texts, text_props,
                       texts_master=ax.legend_.texts, texts_name='legend text')
    else:
        warnings.warn("Trying to set legend text properties but no legend texts were specified.")


def set_log_exponents(ax, which_axes):
    '''
    Set ticklabels as logarithmic exponents on requested x/y axis
    :param ax: [matplotlib.axes] Axis object
    :param which_axes: [str] 'x', 'y', 'both' OR [matplotlib.axis.XAxis, matplotlib.axis.YAxis] (optionally as list)
    :return: None
    '''
    # Get appropriate axis/axes objects from input
    axes_dict = {'x': ax.xaxis, 'y': ax.yaxis}
    which_axes = _get_plot_elements(ax, which_axes, axes_dict,
                                    'Axes',
                                    (matplotlib.axis.XAxis, matplotlib.axis.YAxis),
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


# Get functions - just get everything - user can parse what they want from output

# def get_spine_props(ax, which_spines):
#     spines = self.spines
#     # Convert which_spines to appropriate spine objects
#     try:
#         which_spines = self._convert_to_obj(which_spines, spines)
#     except (IndexError, ValueError) as e:
#         print(e.args[0])
#         return
#     spine_objects = [ax.spines[sp] for sp in which_spines]
#
#     if(which_spines is not None):
#         # Make blank copy of spines_dict that doesn't persist
#         spines_dict = copy.deepcopy(selfspines_dict)
#         spines_dict = self._get_props(ax, spine_objects, spines_dict)
#         return spines_dict
#     else:
#         warnings.warn("Trying to get spine properties but which_spines is None.")

# def get_tick_props(ax, which_axes):

# def get_label_props(ax, which_labels):

# def get_line_props(ax, which_lines, line_type=None):
#     lines = ax.lines if line_type is None else line_type
#     # Convert which_lines to appropriate line objects
#     try:
#         which_lines =self._convert_to_obj(which_lines, lines)
#     except (IndexError, ValueError) as e:
#         print(e.args[0])
#         return
#     if(which_lines is not None):
#         # Make blank copy of lines_dict that doesn't persist
#         lines_dict = copy.deepcopy(self.lines_dict)
#         lines_dict = self._get_props(ax, which_lines, lines_dict)
#         return lines_dict
#     else:
#         warnings.warn("Trying to get line properties but which_lines is None")

# def get_marker_props(ax, which_markers, marker_type):
#     markers = ax.collections if marker_type is None else marker_type
#     # Convert which_markers to appropriate marker objects
#     try:
#         which_markers = self._convert_to_obj(which_markers, markers)
#     except (IndexError, ValueError) as e:
#         print(e.args[0])
#         return
#
#     if(which_markers is not None):
#         # Make blank copy o markers_dict that doesn't persist
#         markers_dict = copy.deepcopy(self.markers_dict)
#         markers_dict = self._get_props(ax, which_markers, markers_dict)
#         # Hack to flatten sizes and paths from a nested list/tuple
#         warnings.warn("Hack to flatten marker sizes is being used. Can it be improved?")
#         markers_dict['sizes'] = [s[0] for s in markers_dict['sizes']]
#         markers_dict['paths'] = [p[0] for p in markers_dict['paths']]
#         return markers_dict

# def get_text_props(self, ax, which_texts, text_type=None):
#     texts = ax.texts if text_type is None else text_type
#     # Convert which_texts into appropriate text objects
#     try
#         which_texts = self._convert_to_obj(which_texts, texts)
#     except (IndexError, ValueError) as e:
#         print(e.args[0])
#         return
#
#     if(which_texts is not None):
#         # Make blank copy of lines_dict that doesn't persist
#         texts_dict = copy.deepcopy(self.texts_dict)
#         texts_dict = self._get_props(ax, which_texts, texts_dict)
#         return texts_dict
#     else:
#         warnings.warn("Trying to get text properties but which_texts is None")

# def get_legend_props(ax):



# Font related functions -----------------------------------------------
def get_available_fonts():
    '''
    Use matplotlib.font_manager to get fonts on system
    :return: Alphabetically sorted list of .ttf fonts
    '''
    import matplotlib.font_manager as fm
    FM = fm.FontManager()
    font_names = set([f.name.encode('utf-8') for f in FM.ttflist])
    return sorted(font_names)


# Private functions ------------------------------------------------------------

def _load_defaults(file='defaults.json'):
    '''
    Load default pyblish plot parameters
    :param file: File where defaults are stored in json format
    :return: Dictionary of parameters
    '''
    with open(file, 'r') as fp:
        data = json.load(fp)
    return data


def _write_defaults(defaults_dict, file='defaults.json'):
    '''
    Write default pyblish plot parameters
    :param defaults_dict: Dictionary of default plot parameters
    :param file:  File where defaults are stored in json format
    :return: None
    '''
    with open(file, 'w') as fp:
        json.dump(defaults_dict, fp, indent=4, sort_keys=True)


def _set_params_defaults(defaults_dict, num_cols):
    '''
    Set plotting parameters dependent on number of columns requested
    :param defaults_dict: [dict] DotDict dictionary (supports dot notation) containing default plotting parameters
    :param num_cols: [int] Number of columns the figure will span in article
    :return: [dict] Updated DotDict dictionary
    '''
    defaults_dict['line_width'] = 1.25 + ((num_cols - 1) * 0.5)
    defaults_dict['marker_size'] = 30 + ((num_cols - 1) * 20)
    defaults_dict['spine_width'] = defaults_dict['line_width']
    defaults_dict['label_size'] = 20 + ((num_cols - 1) * 6)
    defaults_dict['ticklabel_size'] = 14 + ((num_cols - 1) * 4)
    defaults_dict['texts_size'] = 18 + ((num_cols - 1) * 4)
    defaults_dict['legendtext_size'] = 16 + ((num_cols - 1) * 4)

    return defaults_dict


def _set_rcparams_defaults(defaults_dict):
    '''
    Override some default rcParams
    :return: None
    '''
    rcParams = matplotlib.rcParams
    rcParams['axes.unicode_minus'] = defaults_dict.use_unicode_minus  # use smaller minus sign in plots
    rcParams['axes.formatter.use_mathtext'] = defaults_dict.use_mathtext  # use mathtext for scientific notation
    rcParams['figure.dpi'] = defaults_dict.dpi


def _get_aspect_val(aspect):
    '''
    Return a decimal aspect ratio given a desired input
    :param aspect: [str, float, int]
    :return: [float] Aspect ratio
    '''
    aspect_dict = {'square': 1, 'normal': 1.333, 'golden': 1.618, 'widescreen': 1.78}
    # If aspect is a number use it directly
    # Otherwise look up aspect in a dictionary to convert to number
    if(':' in aspect):
        numerator, denominator = aspect.split(':')
        aspect_val = float(numerator)/float(denominator)
    else:
        try:
            float(aspect)
        except ValueError:
            try:
                aspect_val = aspect_dict[aspect]
            except KeyError:
                raise KeyError("Unrecognised aspect - use %s" % ', '.join(aspect_dict.keys()))
        else:
            aspect_val = aspect
    return aspect_val


def _get_figure_size(num_cols, aspect_val):
    '''
    Get size of figure object based on one or two column request
    :param num_cols: Number of column requested
    :param aspect_val: Aspect value of figure
    :return: Figure width and height * 2 in order to produce plots that reduce better
    '''
    fig_width = 3.333 if num_cols == 1 else 7.639  # One column or two columns + middle space
    fig_height = fig_width * 1./aspect_val
    # Return figure size of double width and height to increase resolution
    return fig_width * 2, fig_height * 2

def _set_figure_size(fig, fig_width, fig_height):
    '''
    Set size of figure
    :param fig: [matplotlib.figure.Figure]
    :param fig_width: [float]
    :param fig_height: [float]
    :return: None
    '''
    fig.set_size_inches(fig_width, fig_height, forward=True)  # Force update


def _append_log_text(wa):
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
    # Check for math text anywhere in the axis object children as custom fonts won't work in this case
    for t in [t.get_text() for t in ax.texts] + [ax.get_xlabel(), ax.get_ylabel()]:
        if('$' in t and fontname is not None):
            if(set_mathtext_font(fontname)):
                warnings.warn("Text contains '$' so mathtext font has been custom updated to specified font. "
                          "This will change the appearance of all mathtext.\n"
                          "If you do not want this change run reset_mathtext_font() to revert back to default, "
                          "do not use a custom font, or remove all of the mathtext.")


def _get_plot_elements(ax, which_elems, elem_master, elem_name, elem_type, elem_keys=None):
    '''
    Get list of lines from str or line object input
    :param ax: [matplotlib.axes] Axis object
    :param which_elems: [str] 'colon-dash-comma separated numbers', 'all' OR [matplotlib object] (optionally as list)
    :param elem_type: [matplotlib.lines.Line2D] Type of line(s) to process
                        e.g. plot lines = ax.lines
                        e.g. legend lines = ??
    :param elem_keys: [list] Keys to use for indexing of elem_master if type(elem_master) is dict
    :return: [list] Plot object(s) of type requested
    '''

    if(which_elems == 'all'):
        which_elems = elem_master
    else:
        which_elems = utils.get_iterable(which_elems)

    get_elems = []
    try:
        for e in which_elems:
            if(isinstance(e, int)):
                get_elems.append(elem_master[e])
            elif(isinstance(e, str)):
                # If input is all numbers and '-'/':' then parse input into index rangs
                if(all([(c.isdigit() or c in [':', '-']) for c in e])):
                    inds = utils.parse_str_ranges(e)
                    for i in inds:
                        # If master list is a dict then use input as index of keys for index of master list
                        if(elem_keys):
                            get_elems.append(elem_master[elem_keys[i]])
                        # Otherwise use input as index of master list
                        else:
                            get_elems.append(elem_master[i])
                # Otherwise use input as index
                else:
                    get_elems.append(elem_master[e])
            elif(isinstance(e, elem_type)):
                get_elems.append(e)
            else:
                raise ValueError
    except (KeyError, ValueError, TypeError):
        if(elem_keys):
            print("Input error: {}. Enter 'all', [".format(elem_name) +
                  ', '.join(["'{}'".format(k) for k in elem_keys]) +
                  "] as a list or individually, or {} object(s).".format(elem_name))
            return
        else:
            print("Input error: {}. Enter 'all', ".format(elem_name) +
                  "a comma-dash-colon separated range of numbers (e.g. '0-2,4'), " +
                  "or {} object(s).".format(elem_name))
            return
    except IndexError:
        print("Input error: {}. ".format(elem_name) +
              "Range exceeds number of {} objects plotted ({}).".format(elem_name, len(elem_master)))
        return
    return get_elems


def _get_marker_paths(symbols, top_level=True):
    '''
    Convert marker symbols or objects into path objects recursively
    :param symbols: [str|tuple|list] Marker identifier (optionally nested)
    :param no_tuple: [bool] Tuple expansion is not needed for nested symbols
    :return: Paths objects
    '''
    paths = symbols
    for i, s in enumerate(symbols):
        if(isinstance(s, list)):
            s = _get_marker_paths(s, False)
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
        warnings.warn("Can not access private variable {}. Matplotlib may have been updated and changed this variable. "
                  "If you want to set legend properties this variable must now be given in 'frame_props'.".format(re.findall("'_.+'", e.args[0])[-1]))
        var = None

    if(frame_props):
        return frame_props.get(var_name, var)
    else:
        return var


def _set_props(ax, obj, **kwargs):
    '''
    Sets object property for each kwarg
    :param ax: [matplotlib.axes] Axis object
    :param obj: [list] Objects to apply property changes to
    :param kwargs: Properties to set
    :return: None
    '''
    # Remove empty keys to avoid trying to set plot parameters to None
    kwargs = utils.remove_empty_keys(kwargs)
    # Convert properties to lists, map lists to length of obj list
    kwargs = {k: utils.map_array(utils.get_iterable(v), len(obj)) for k,v in kwargs.items()}
    # Set object properties
    for k in kwargs:
        for w, kv in zip(obj, kwargs.get(k)):
            plt.setp(w, **{k: kv})


def _get_props(self, ax, obj, prop_dict):
    '''
    Return a dictionary of an object's properties in specified dictionary keys
    :param ax:
    :param obj:
    :param dict:
    :return:
    '''
    for d in prop_dict:
        for o in obj:
            prop = plt.getp(o, d)
            # Append property to appropriate dictionary key entry
            # Only append first entry if list or tuple
            prop_dict[d].append(prop)
    return prop_dict

