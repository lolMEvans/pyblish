from __future__ import print_function

import ast
import copy
import re
import warnings
from collections import OrderedDict
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import math
import yaml

# ToDo: Main
# Revert back to the normal functions because Class doesn't really make sense here...

# Add complementary get functions to every set function
# Separate code into different files - leads back to maybe split classes up and have pyblishify inherit?

# Set custom colour cycle for lines to nice sequence - get my ColorMapper module from laptop!

from dotmap import DotMap

import utils


def _load_defaults(file='defaults.yaml'):
    '''
    Load default pyblish plot parameters
    :param file: File where defaults are stored in yaml format
    :return: Dictionary of parameters that can be accessed using dot notation
    '''
    with open(file, 'r') as fp:
        data = yaml.load(fp)
    return DotMap(data)

def pyblishify(fig, num_cols, aspect='square', which_labels='both', which_ticks='both',
                   which_spines=['left', 'bottom'],
                   which_lines='all', which_markers='all', which_texts='all',
                   which_legend_handles='all', which_legend_labels='all',
                   change_log_scales=True):

    defaults_dict = _load_defaults()
    # Set defaults that are dependent on number of columns requested
    defaults_dict = _set_defaults_pars(defaults_dict, num_cols)
    # Override a selection of default rcParams
    _set_rcparams()
    # Set mathtext font
    set_mathtext_font(defaults_dict.default_mathtext)


    # Convert aspect variable to number
    aspect_val = _get_aspect_val(aspect)
    # Set figure size
    fig_width, fig_height = _get_figure_size(num_cols, aspect_val)
    set_figure_size(fig, fig_width, fig_height)

    # Apply changes to all axis objects in figure
    for ax in fig.axes:

        # Set axes label properties
        if(which_labels is not None):
            set_label_props(ax, 'both',
                            label_props=dict(fontsize=defaults_dict.label_size*3, fontname=None, color=None))

        # Set axes ticks and ticklabel properties
        if(which_ticks is not None):
            set_tick_props(ax, 'both',
                           tick_props=dict(size=defaults_dict.majortick_size, width=defaults_dict.line_width, color='green',
                                           direction=defaults_dict.tick_dir, pad=defaults_dict.ticklabel_pad,
                                           labelsize=defaults_dict.ticklabel_size, labelcolor='purple'),
                           tick_type='major')
            set_tick_props(ax, 'both',
                           tick_props=dict(size=defaults_dict.minortick_size, width=defaults_dict.line_width, color='blue',
                                           direction=defaults_dict.tick_dir, pad=defaults_dict.ticklabel_pad,
                                           labelsize=defaults_dict.ticklabel_size, labelcolor='red'),
                           tick_type='minor')

        # Set axes log scale properties
        if(change_log_scales):
            set_log_exponents(ax, 'both')

        # Set axes spine properties
        if(which_spines is not None):
            set_spine_props(ax, ['left', 'bottom', 'right'],
                            spine_props=dict(
                                             linewidth=defaults_dict.spine_width,
                                             edgecolor='blue'))
        # Set plotted line or marker properties *** DONE ***
        if(which_lines is not None):
            if(ax.lines):
                set_line_props(ax, 'all',
                               line_props=dict(
                                               linewidth=defaults_dict.line_width*2,
                                               color=defaults_dict.col_cycle,
                                               linestyle='-'))

        if(which_markers is not None):
            if(ax.collections):
                set_marker_props(ax, 'all',
                                      marker_props=dict(
                                              sizes=100,#defaults_dict.marker_size,
                                              linewidth=defaults_dict.line_width,
                                              linestyle=[['-', ':']],
                                              facecolor=[defaults_dict.col_cycle],
                                              edgecolor=[defaults_dict.col_cycle],
                                             symbols='o'))
    #
    #     # Set legend properties *** DONE ***
    #     if(ax.get_legend() and (ax.lines or ax.collections)):
    #         # Get properties of lines and markers on plot as dictionaries of attribute names
    #         # to send through to legend handles
    #         if(which_lines is not None):
    #             line_props = self.get_line_props(ax, which_lines, ax.lines)
    #         else:
    #             line_props = None
    #         if(which_markers is not None):
    #             marker_props = self.get_marker_props(ax, which_markers, ax.collections)
    #         else:
    #             marker_props = None
    #         self.set_legend_props(ax, ax.get_legend().legendHandles,
    #                               handle_line_props=line_props,
    #                               handle_marker_props=marker_props,
    #                               handle_text_props=dict(
    #                                       fontsize=self.legendtext_size,
    #                                       color=None,
    #                                       fontname=None),
    #                               legend_props=dict(
    #                                       loc='upper center',
    #                                       ncol=5,
    #                                       columnspacing=0.9,
    #                                       labelspacing=1.0,
    #                                       handlelength=1.0,
    #                                       numpoints=1,
    #                                       scatterpoints=1,
    #                                       frameon=False))
    #
        # Set text properties (added with ax.text) *** DONE ***
        if(which_texts is not None):
            set_text_props(ax, which_texts,
                                text_props=dict(
                                        fontsize=defaults_dict.texts_size,
                                        color='green',
                                        fontname='Arial'))


def set_figure_size(fig, fig_width, fig_height):
    '''
    Set figure size
    :param fig: [matplotlib.figure.Figure]
    :param fig_width: [float]
    :param fig_height: [float]
    :return: None
    '''
    _set_figure_size(fig, fig_width, fig_height)


def _set_defaults_pars(defaults_dict, num_cols):
    '''
    Set plotting parameters dependent on number of columns requested
    :param defaults_dict: [dict] DotMap dictionary (supports dot notation) containing default plotting parameters
    :param num_cols: [int] Number of columns the figure will span in article
    :return: [dict] Updated DotMap dictionary
    '''
    defaults_dict['line_width'] = 1.25 + ((num_cols - 1) * 0.5)
    defaults_dict['marker_size'] = 30 + ((num_cols - 1) * 20)
    defaults_dict['spine_width'] = defaults_dict['line_width']
    defaults_dict['label_size'] = 20 + ((num_cols - 1) * 6)
    defaults_dict['ticklabel_size'] = 14 + ((num_cols - 1) * 4)
    defaults_dict['texts_size'] = 18 + ((num_cols - 1) * 4)
    defaults_dict['legendtext_size'] = 16 + ((num_cols - 1) * 4)

    return defaults_dict

def _set_rcparams():
    '''
    Override some default rcParams
    :return: None
    '''
    rcParams = matplotlib.rcParams
    # rcParams are updated after everything plotted on figure
    # so rcParams that override plotting (e.g. prop_cycle)
    # need to be assigned before figure object created
    rcParams['axes.unicode_minus'] = False  # use smaller minus sign in plots
    rcParams['axes.formatter.use_mathtext'] = True  # use mathtext for scientific notation
    rcParams['figure.dpi'] = 300

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


def _get_axes(ax, which_axes):
    '''
    Get list of x/y axis objects from str or x/y axis object input
    :param ax: [matplotlib.axes] Axis object
    :param which_axes: [str] 'x', 'y', 'both' OR [matplotlib.axis.XAxis, matplotlib.axis.YAxis] (optionally as list)
    :return: [list] x/y axis object(s)
    '''
    # Convert which_axes object into iterable
    if(which_axes == 'both'):
        which_axes = ['xaxis', 'yaxis']
    else:
        which_axes = utils.get_iterable(which_axes)
    # Get appropriate axis object for each entry in which_axes
    axes = []
    try:
        for i in which_axes:
            if(type(i) is str):
                axes.append(getattr(ax, i))
            elif(type(i) in [matplotlib.axis.XAxis, matplotlib.axis.YAxis]):
                axes.append(i)
            else:
                raise ValueError
    except (ValueError, AttributeError):
        print("Unrecognised axis. Enter 'x', 'y', 'both' "
                         "or axis object/axes objects")
        return None
    return axes


def set_label_props(ax, which_axes,
                    label_props=dict(fontsize=None, fontname=None, color=None)):
    '''
    Set properties for axes labels
    :param ax: [matplotlib.axes] Axis object
    :param which_axes: [str] 'x', 'y', 'both' OR [matplotlib.axis.XAxis, matplotlib.axis.YAxis] (optionally as list)
    :param label_props: [dict] Label properties
    :return: None
    '''
    # Check if there's mathtext if user requests a custom font as it will change font for
    # all mathtext in the plot
    if('fontname' in label_props):
        _check_mathtext(ax, label_props['fontname'])
    # Get appropriate axis/axes objects from input
    which_axes = _get_axes(ax, which_axes)
    # Get corresponding axis label(s)
    which_labels = [wa.label for wa in which_axes]
    # Set label properties
    if(which_labels):
        _set_props(ax, which_labels, **label_props)
    else:
        warnings.warn("Trying to set label properties but no axes were specified.")


def set_tick_props(ax, which_axes,
                   tick_props=dict(size=None, width=None, _color=None,
                                   direction=None, pad=None,
                                   labelsize=None, labelcolor=None),
                   tick_type='major'):
    '''
    Set properties for axes ticks
    :param ax: [matplotlib.axes] Axis object
    :param which_axes: [str] 'x', 'y', 'both' OR [matplotlib.axis.XAxis, matplotlib.axis.YAxis] (optionally as list)
    :param ticks_props: [dict] Tick properties
    :param tick_type: [str] 'major' or 'minor'
    :return: None
    '''
    # Get appropriate axis/axes objects from input
    which_axes = _get_axes(ax, which_axes)
    # Set tick properties
    if(which_axes):
        tick_props = utils.remove_empty_keys(tick_props)
        for wa in which_axes:
            wa.set_tick_params(tick_type, **tick_props)
    else:
        warnings.warn("Trying to set tick properties but no axes were specified.")


def set_spine_props(ax, which_spines,
                    spine_props=dict(linewidth=None, edgecolor=None),
                    hide_other_spines=True,
                    duplicate_ticks=False):
    '''
    Set properties for spines
    :param ax: [matplotlib.axes] Axis object
    :param which_spines: [str] 'left', 'bottom', 'right', 'top' OR [matplotlib.spines.Spine] (optionally as list)
    :param spine_props: [dict] Spine properties
    :param hide_other_spines: [bool] Unspecified spines are hidden if set
    :param duplicate_ticks: [bool] Ticks are not duplicated on each side (when both sides of spines are visible) if set
    :return: None
    '''
    spines = ax.spines
    spines_dict = {'left': ax.yaxis, 'bottom': ax.xaxis, 'right': ax.yaxis, 'top': ax.xaxis}
    # Get appropriate spine object(s) from input
    which_spines = _get_plot_elements(ax, which_spines, ax.spines, matplotlib.spines.Spine, ['left', 'bottom', 'right', 'top'])
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

    if(which_spines):
        _set_props(ax, which_spines, **spine_props)
        # Hide unspecified spines
        if(hide_other_spines):
            _set_props(ax, which_spines_invis, visible=False)
    else:
        warnings.warn("Trying to set spine properties but no spines were specififed.")

# def get_spine_props(self, ax, which_spines):
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


def _get_plot_elements(ax, which_elems, elem_master, elem_type, elem_keys=None):
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
            if(type(e) is str):
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
            elif(type(e) is elem_type):
                get_elems.append(e)
            else:
                raise ValueError
    except (ValueError, AttributeError):
        print("Unrecognised object. Enter 'all', a range such as '0:3' "
                         "or {} object/axes objects.".format(elem_type))
        return None
    except (IndexError, KeyError):
        print("Attempted to access a {} that doesn't exist. "
              "The input range can only span across the number of {}s plotted ({}).".format(elem_type, elem_type, len(elem_master)))
    except TypeError:
        print("Unrecognised input. Check for errors.")
    return get_elems


def set_line_props(ax, which_lines,
                    line_props=dict(linewidth=None, color=None, linestyle=None),
                    **kwargs):
    '''
    Set properties for plotted lines
    :param ax: [matplotlib.axes] Axis object
    :param which_lines: [str] 'colon-dash-comma separated numbers', 'all' OR [matplotlib.lines.Line2D] (optionally as list)
    :param line_props: [dict] Line properties
    :param kwargs:
    :return: None
    '''
    # ToDo: Is this necessary? Do we use any other lines than ax.lines?
    lines_master = kwargs.get('line_type', ax.lines)
    # Get appropriate line object(s) from input
    which_lines = _get_plot_elements(ax, which_lines, lines_master, matplotlib.lines.Line2D)
    # Set line properties
    if(which_lines is not None):
        _set_props(ax, which_lines, **line_props)
    else:
        warnings.warn("Trying to set line properties but no lines were specified.")

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


# def get_line_props(self, ax, which_lines, line_type=None):
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


def _get_marker_paths(symbols, top_level=True):
    '''
    Convert marker symbols or objects into path objects recursively
    :param symbols: [str, tuple, list] Marker identifier (optionally nested)
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

def set_marker_props(ax, which_markers,
                     marker_props=dict(sizes=None, linewidth=None, linestyle=None,
                                      facecolor=None, edgecolor=None, symbols=None),
                     **kwargs):
    '''
    Set properties for plotted markers
    :param ax: [matplotlib.axes] Axis object
    :param which_markers: [str] 'colon-dash-comma separated numbers', 'all'
    OR [matplotlib.collections.PathCollection] (optionally as list)
    :param marker_props: [dict] Marker properties
        sizes, linewidth, linestyle, facecolor, edgecolor can be nested lists in order to
        change properties of individual markers within marker collections
    :param kwargs:
    :return: None
    '''
    markers_master = kwargs.get('marker_type', ax.collections)
    # Get appropriate marker object(s) from input
    which_markers = _get_plot_elements(ax, which_markers, markers_master, matplotlib.collections.PathCollection)

    # Convert sizes input to a nested list as this is the input for each collection in set_sizes()
    # This means incidentally that individual marker sizes can be set within each collection
    try:
        if(type(marker_props['sizes']) is not list or not any([isinstance(i, list) for i in marker_props['sizes']])):
            marker_props['sizes'] = [[s] for s in utils.get_iterable(marker_props['sizes'])]
    except KeyError:
        pass

    marker_props['paths'] = _get_marker_paths(utils.get_iterable(marker_props['symbols']))
    marker_props.pop('symbols')  # Remove symbols key as it is now paths
    # Set marker properties
    if(which_markers):
        _set_props(ax, which_markers, **marker_props)
    else:
        warnings.warn("Trying to set marker properties but no markers were specified.")


    # def get_marker_props(self, ax, which_markers, marker_type):
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

def set_text_props(ax, which_texts,
                   text_props=dict(fontsize=None, color=None, fontname=None),
                   **kwargs):
    '''
    Set properties for plotted texts
    :param ax: [matplotlib.axes] Axis object
    :param which_texts: [str] 'colon-dash-comma separated numbers', 'all' OR [matplotlib.text.Text] (optionally as list)
    :param line_props: [dict] Text properties
    :param kwargs:
    :return: None
    '''
    texts_master = kwargs.get('texts_master', ax.texts)
    # Get appropriate text object(s) from input
    which_texts = _get_plot_elements(ax, which_texts, texts_master, matplotlib.text.Text)

    # Set text properties
    if(which_texts is not None):
        _set_props(ax, which_texts, **text_props)
    else:
        warnings.warn("Trying to set text properties but no texts were specified.")

    # def get_text_props(self, ax, which_texts, text_type=None):
    #     texts = ax.texts if text_type is None else text_type
    #     # Convert which_texts into appropriate text objects
    #     try:
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

    def set_legend_props(self, ax, which_handles,
                            handle_line_props=dict(linewidth=None, color=None, linestyle=None),
                            handle_marker_props=dict(sizes=None, linewidth=None, linestyle=None,
                                          facecolor=None, edgecolor=None, paths=None),
                            handle_text_props=dict(fontsize=None, color=None),
                            legend_props=dict(loc=None, ncol=None, columnspacing=None, labelspacing=None,
                                              handlelength=1.0, numpoints=None, scatterpoints=None,
                                              frameon=None)):
        '''
        Set kwarg properties of legend (e.g. position, handlelength, ncol, columnspacing etc)
            Note: All non-default parameters must be set in legend_props, not just the one to set,
                  because a new legend is drawn for this which uses default values for parameters not set
                  These default values can be changed in rcParams
        Set handles of axis legend - both lines and markers and text

        :param ax:
        :param which_handles:
        :param handle_widths:
        :param handle_colors:
        :param handle_styles:
        :return:
        '''

        legend = ax.get_legend()
        # Update legend kwarg properties (e.g. position, handlelength, ncol, columnspacing etc)
        if(all([lv is not None for lp, lv in legend_props.iteritems()])):
            # Get existing bbox coords in axes coordinates
            bbox_axcoords = ax.transAxes.inverted().transform(legend.get_bbox_to_anchor().get_points())
            bbox_x0, bbox_y0 = bbox_axcoords[0][0], bbox_axcoords[0][1]
            # Redraw legend with updated init parameters (e.g. handlelength, columnspacing etc)
            handles, labels = legend.legendHandles, [l.get_text() for l in legend.texts]
            new_legend = ax.legend(handles, labels, bbox_to_anchor=(bbox_x0, bbox_y0),
                          **legend_props)
            legend = new_legend

        handles = legend.legendHandles
        # Convert which_handles into appropriate handle objects
        # and update to handles even if which_handles' entries don't match (update_unmatching)
        # so that can target new legend's handles correctly instead of old ones if handle objects were passed in
        try:
            which_handles = self._convert_to_obj(which_handles, handles, update_unmatching=True)
        except (IndexError, ValueError) as e:
            print(e.args[0])
            return

        handle_lines = [hl for hl in legend.legendHandles if isinstance(hl, matplotlib.lines.Line2D)]
        handle_markers = [hm for hm in legend.legendHandles if isinstance(hm, matplotlib.collections.PathCollection)]
        handle_texts = legend.texts

        which_handle_lines = [whl for whl in which_handles if isinstance(whl, matplotlib.lines.Line2D)]
        which_handle_markers = [whm for whm in which_handles if isinstance(whm, matplotlib.collections.PathCollection)]
        # Get texts at relative indexes of lines and markers
        which_handle_texts = [handle_texts[which_handles.index(whl)] for whl in which_handle_lines] \
                                + [handle_texts[which_handles.index(whm)] for whm in which_handle_markers]

        # Set legend handle lines if they exist
        if(which_handle_lines and handle_line_props):
            if(all([lhl is not None for lh, lhl in handle_line_props.iteritems()])):
                self.set_line_props(ax, which_handle_lines, line_type = handle_lines,
                                    line_props=handle_line_props)
            else:
                warnings.warn("Legend lines have been requested but no legend line parameters are set.")
        # Set legend handle markers if they exist
        if(which_handle_markers and handle_marker_props):
            if(all([lhm is not None for lh, lhm in handle_marker_props.iteritems()])):
                self.set_marker_props(ax, which_handle_markers, marker_type=handle_markers,
                                      marker_props=handle_marker_props)
            else:
                warnings.warn("Legend markers have been requested but no legend marker parameters are set.")
        # Set legend handle text (guaranteed to exist if legend exists)
        self.set_text_props(ax, which_handle_texts, text_type=legend.texts,
                            text_props=handle_text_props)

    def get_legend_props(self, ax):
        pass

def set_log_exponents(ax, which_axes):
    '''
    Set ticklabels as logarithmic exponents on requested x/y axis
    :param ax: [matplotlib.axes] Axis object
    :param which_axes: [str] 'x', 'y', 'both' OR [matplotlib.axis.XAxis, matplotlib.axis.YAxis] (optionally as list)
    :return: None
    '''
    # Get appropriate axis/axes objects from input
    which_axes = _get_axes(ax, which_axes)
    if(which_axes):
        for wa in which_axes:
            # Check if axis scale is logarithmic or all tick labels are scientific notation
            # because in these cases we can assume exponential notation will be good
            if(wa.get_scale() == 'log' or all(['e' in str(t) for t in wa.get_majorticklocs()])):
                # Change exponentials notation to log notation - i.e. 10^2, 10^3 -> 2, 3
                wa.set_major_formatter(FuncFormatter(exp_to_log))
                # Add log to label text if it's absent
                _append_log_text(wa)

# Font related functions -----------------------------------------------
def get_available_fonts():
    '''
    Use matplotlib.font_manager to get fonts on system so that user can see what fonts are available for
    set_texts_props (text_font)
    :return: Alphabetically sorted list of ttf fonts
    '''
    import matplotlib.font_manager as fm
    FM = fm.FontManager()
    font_names = set([f.name.encode('utf-8') for f in FM.ttflist])
    return sorted(font_names)


# Private functions ------------------------------------------------------------


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
def _convert_to_list(self, input_val):
    '''
    Convert function argument into list
    '''
    input_type = type(input_val)
    if (input_type == list):
        list_input = input_val
    elif (input_val is None):
        list_input = [None]
    else:
        list_input = [input_val]
        #raise ValueError("Argument must be an integer, float, string or boolean value")
    return list_input
def _convert_to_obj(self, input_val, obj_default, update_unmatching=False):
    input_type = type(input_val)
    if(input_type == list):
        if (len(input_val) > len(obj_default)):
            raise ValueError("Too many objects.\n"
                             "Only %d maximum can be provided." % len(obj_default))
        # Check that input doesn't contain any foreign entries
        if (any([i not in obj_default for i in input_val])):
            if(update_unmatching):
                return obj_default
            else:
                raise ValueError("Unrecognised object.\n"
                             "Only %s are accepted." % ', '.join(str(o) for o in obj_default))
        else:
            return input_val
    elif(input_type == int):
        if(input_val >= 0):
            return [obj_default[input_val]]
        else:
            return obj_default[:input_val]
    elif(input_type == float):
        raise IndexError("Object identifier index can not be a float.")
    elif(input_type == str):
        if (input_val in obj_default):
            return [input_val]
        elif (input_val.lower() == 'all'):
            return obj_default
        else:
            list_out = []
            input_val = re.sub('(\d)-(\d)', self._sub_range, input_val)
            if(re.sub(',', '', input_val).isdigit()):
                try:
                    print(input_val)
                    list_out.extend([obj_default[int(i)] for i in input_val.split(',')])
                except:
                    raise IndexError("Index is out of range.\n"
                                     "Only index up to %d can be provided." % len(obj_default))
                else:
                    return list_out
            else:
                raise ValueError("Unrecognised value.\n"
                             "Only %s are accepted." % ', '.join(str(o) for o in obj_default))
    # Convert input into list if it is the same as default object and not common type
    elif(input_type == type(obj_default)):
        return [input_val]
    elif(input_val is None):
        return None
    else:
        raise ValueError("Object identifier not recognised.")
def _sub_range(self, match_obj):
    match_range = (range(int(match_obj.group(1)), int(match_obj.group(2)) + 1))
    return ','.join([str(m) for m in match_range])



    # Put this in utils along with functions at bottom
def exp_to_log(x, p):
    return "{:.0f}".format(math.log10(x))
