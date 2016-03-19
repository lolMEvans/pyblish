from __future__ import print_function

import ast
import copy
import re
import warnings

import matplotlib.pyplot as plt
import matplotlib

# ToDo: Main
# Revert back to the normal functions because Class doesn't really make sense here...

# Add complementary get functions to every set function
# Separate code into different files - leads back to maybe split classes up and have pyblishify inherit?

# Set custom colour cycle for lines to nice sequence - get my ColorMapper module from laptop!

from matplotlib.ticker import FuncFormatter
import math

# Put this in utils along with functions at bottom
def exp_to_log(x, p):
    return "{:.0f}".format(math.log10(x))

def json_create(data_dict):
    import json
    with open('data.json', 'w') as fp:
        json.dump(data_dict, fp, indent=4)


class Pyblishify(object):
    def __init__(self):
        self.majortick_size = 6.0
        self.minortick_size = 4.0
        self.tick_dir = 'out'
        self.ticklabel_pad = -5
        self.spines = ['left', 'bottom', 'right', 'top']
        self.spine_col = 'black'
        self.line_style = '-'
        self.col_array = ['red', 'orange', 'yellow', 'green', 'blue', 'purple']  # Custom color cycle!

        # Define dictionaries to use for axis object lookup
        self.axis_dict = {'x':'ax.xaxis', 'y':'ax.yaxis', 'both':'[ax.xaxis, ax.yaxis]'}
        self.spine_axis_dict = {'left': 'ax.yaxis', 'top': 'ax.xaxis', 'right': 'ax.yaxis', 'bottom': 'ax.xaxis'}

        # Define empty dictionary templates of most important spine, line and marker properties that can be
        # retrieved using plt.setp - these are deep copied in respective get functions
        self.spines_dict = {'linewidth': [], 'facecolor': [], 'edgecolor': [],'linestyle': [], 'visible': []}
        self.lines_dict = {'linewidth': [], 'color': [], 'linestyle': []}
        self.markers_dict = {'paths': [], 'sizes': [], 'linewidth': [], 'linestyle':[], 'facecolor': [], 'edgecolor': []}
        self.texts_dict = {'fontsize': [], 'color': [], 'fontname': []}
        self.default_mathtext = 'stixsans'

    def pyblishify(self, fig, num_cols, aspect='square', which_labels='both', which_ticks='both',
                   which_spines=['left', 'bottom'],
                   which_lines='all', which_markers='all', which_texts='all',
                   which_legend_handles='all', which_legend_labels='all',
                   change_log_scales=True):

        # Set parameters dependent on number of columns requested
        self._set_pars(num_cols)
        # Set some rcParams (e.g. fig dpi, no unicode minus)
        self._set_mnras_pars()
        # Set mathtext font
        self.set_mathtext_font(self.default_mathtext)

        # Convert aspect variable to number
        aspect_val = self._get_aspect_val(aspect)
        # Set figure size
        fig_width, fig_height = self._get_figure_size(num_cols, aspect_val)
        self.set_figure_size(fig, fig_width, fig_height)

        # Apply changes to all axis objects in figure
        for ax in fig.axes:

            # Set axes label properties
            if(which_labels is not None):
                self.set_label_props(ax, 'both',
                                    label_props=dict(fontsize=self.label_size, fontname=None))

            # Set axes ticks and ticklabel properties *** DONE ***
            if(which_ticks is not None):
                self.set_tick_props(ax, 'both',
                                    tick_props=dict(size=self.majortick_size, width=self.line_width, color='red',
                                                direction=self.tick_dir, pad=self.ticklabel_pad,
                                                labelsize=self.ticklabel_size, labelcolor='red'
                                                ),
                                    tick_type='major')
                self.set_tick_props(ax, 'both',
                                    tick_props=dict(size=self.minortick_size, width=self.line_width, color='red',
                                                direction=self.tick_dir, pad=self.ticklabel_pad,
                                                labelsize=self.ticklabel_size, labelcolor='red'
                                                ),
                                    tick_type='minor')

            # Set axes log scale properties
            if(change_log_scales):
                self.set_log_scale(ax, 'both')

            # Set axes spine properties *** DONE ***
            if(which_spines is not None):
                self.set_spine_props(ax, which_spines,
                                        spine_props=dict(
                                                  linewidth=self.spine_width,
                                                  edgecolor='red'))
            # Set plotted line or marker properties *** DONE ***
            if(which_lines is not None):
                if(ax.lines):
                    self.set_line_props(ax, which_lines,
                                        line_props=dict(
                                                  linewidth=self.line_width,
                                                  color=self.col_array,
                                                  linestyle='-'))

            if(which_markers is not None):
                if(ax.collections):
                    self.set_marker_props(ax, which_markers,
                                          marker_props=dict(
                                                  sizes=self.marker_size,
                                                  linewidth=self.line_width,
                                                  linestyle='-',
                                                  facecolor=self.col_array,
                                                  edgecolor=self.col_array,
                                                  paths=None))

            # Set legend properties *** DONE ***
            if(ax.get_legend() and (ax.lines or ax.collections)):
                # Get properties of lines and markers on plot as dictionaries of attribute names
                # to send through to legend handles
                if(which_lines is not None):
                    line_props = self.get_line_props(ax, which_lines, ax.lines)
                else:
                    line_props = None
                if(which_markers is not None):
                    marker_props = self.get_marker_props(ax, which_markers, ax.collections)
                else:
                    marker_props = None
                self.set_legend_props(ax, ax.get_legend().legendHandles,
                                      handle_line_props=line_props,
                                      handle_marker_props=marker_props,
                                      handle_text_props=dict(
                                              fontsize=self.legendtext_size,
                                              color=None,
                                              fontname=None),
                                      legend_props=dict(
                                              loc='upper center',
                                              ncol=5,
                                              columnspacing=0.9,
                                              labelspacing=1.0,
                                              handlelength=1.0,
                                              numpoints=1,
                                              scatterpoints=1,
                                              frameon=False))

            # Set text properties (added with ax.text) *** DONE ***
            if(which_texts is not None):
                self.set_text_props(ax, which_texts,
                                    text_props=dict(
                                            fontsize=self.texts_size,
                                            color='green',
                                            fontname=None))



    def set_figure_size(self, fig, fig_width, fig_height):
        fig.set_size_inches(fig_width, fig_height, forward=True) # Force update

    def get_figure_size(self, fig):
        return fig.get_size_inches()

    def set_label_props(self, ax, which_labels,
                        label_props=dict(fontsize=None, fontname=None)):
        # Only accept 'x', 'y' or 'both' for which_labels and get appropriate array from axis dictionary
        try:
            # eval is used as dictionary stores axis objects as string names
            which_labels = eval(self.axis_dict[which_labels], {}, {'ax':ax})
        except KeyError:
            print("Unrecognised value.\n"
                  "Only %s are accepted." % ', '.join(str(t) for t in self.axis_dict))
            return

        # Check if there's mathtext if user requests a custom font as it will change font for
        # all mathtext in the plot as it's an rcParam
        if('fontname' in label_props):
            self._check_mathtext(ax, label_props['fontname'])

        label_props = self._remove_empty_keys(label_props)
        for ax_dir in which_labels:
            ax_dir.set_label_text(ax_dir.get_label_text(), **label_props)

    def set_tick_props(self, ax, which_axes,
                       tick_props=dict(size=None, width=None, color=None,
                                       direction=None, pad=None,
                                       labelsize=None, labelcolor=None),
                       tick_type='major'):
        # Only accept 'x', 'y' or 'both' for which_axes and get appropriate array from axis dictionary
        try:
            # eval is used as dictionary stores axis objects as string names
            which_axes = eval(self.axis_dict[which_axes], {}, {'ax':ax})
        except KeyError:
            print("Unrecognised value.\n"
                  "Only %s are accepted." % ', '.join(str(t) for t in self.axis_dict))
            return
        tick_props = self._remove_empty_keys(tick_props)
        for ax_dir in which_axes:
            ax_dir.set_tick_params(tick_type, **tick_props)

    def set_spine_props(self, ax, which_spines,
                        spine_props=dict(linewidth=None, edgecolor=None),
                        hide_other_spines=True,
                        duplicate_ticks=False):
        '''
        Set properties of spines in order top, right, bottom, left
        First spine is assigned the tick labels unless duplicate_ticks is True
        Edits spines specified by which_spines and hides those not specified
        Colours ticks and ticklabels the same colour as appropriate spines
        '''

        # Check spine names are allowed
        spines = self.spines
        # Dictionary to allow ticks to be hidden as well as spines
        opp_dict = self.spine_axis_dict
        # Convert which_spines into appropriate spine objects
        try:
            which_spines = self._convert_to_obj(which_spines, spines)
        except (IndexError, ValueError) as e:
            print(e.args[0])
            return
        spine_objects = [ax.spines[sp] for sp in which_spines]
        # List of unspecified spine objects
        spine_objects_invisible = [ax.spines[sp] for sp in set(spines) if sp not in set(which_spines)]

        # Turn off all spines and ticks and labels initially
        for sp in spines:
            # eval is used as dictionary stores axis objects as string names
            ax_dir = eval(opp_dict[sp], {}, {'ax':ax})
            ax_dir.set_tick_params(which='both', **{sp: 'off'})
            ax_dir.set_tick_params(**{'label' + sp: 'off'})
        # Turn on specified spine ticks and labels in order given
        for wsp in which_spines[::-1]:
            # eval is used as dictionary stores axis objects as string names
            ax_dir = eval(opp_dict[wsp], {}, {'ax':ax})
            ax_dir.set_tick_params(**{wsp: 'on'})
            ax_dir.set_tick_params(**{'label' + wsp: 'on'})
            # Avoid duplication of tick labels unless requested
            if not (duplicate_ticks):
                ax_dir.set_ticks_position(wsp)
        # Set spine properties
        if(which_spines is not None):
            self._set_props(ax, spine_objects, **spine_props)
            # Turn off unspecified spines
            if(hide_other_spines):
                self._set_props(ax, spine_objects_invisible, visible=False)
        else:
            warnings.warn("Trying to set spine properties but which_spines is None.")

    def get_spine_props(self, ax, which_spines):
        spines = self.spines
        # Convert which_spines to appropriate spine objects
        try:
            which_spines = self._convert_to_obj(which_spines, spines)
        except (IndexError, ValueError) as e:
            print(e.args[0])
            return
        spine_objects = [ax.spines[sp] for sp in which_spines]

        if(which_spines is not None):
            # Make blank copy of spines_dict that doesn't persist
            spines_dict = copy.deepcopy(self.spines_dict)
            spines_dict = self._get_props(ax, spine_objects, spines_dict)
            return spines_dict
        else:
            warnings.warn("Trying to get spine properties but which_spines is None.")

    def set_line_props(self, ax, which_lines,
                        line_props=dict(linewidth=None, color=None, linestyle=None),
                        line_type=None):
        lines = ax.lines if line_type is None else line_type
        # Convert which_lines into appropriate line objects
        try:
            which_lines = self._convert_to_obj(which_lines, lines)
        except (IndexError, ValueError) as e:
            print(e.args[0])
            return
        # Set line properties
        if(which_lines is not None):
            self._set_props(ax, which_lines, **line_props)
        else:
            warnings.warn("Trying to set line properties but which_lines is None.")

    def get_line_props(self, ax, which_lines, line_type=None):
        lines = ax.lines if line_type is None else line_type
        # Convert which_lines to appropriate line objects
        try:
            which_lines = self._convert_to_obj(which_lines, lines)
        except (IndexError, ValueError) as e:
            print(e.args[0])
            return

        if(which_lines is not None):
            # Make blank copy of lines_dict that doesn't persist
            lines_dict = copy.deepcopy(self.lines_dict)
            lines_dict = self._get_props(ax, which_lines, lines_dict)
            return lines_dict
        else:
            warnings.warn("Trying to get line properties but which_lines is None")

    def set_marker_props(self, ax, which_markers,
                         marker_props=dict(sizes=None, linewidth=None, linestyle=None,
                                          facecolor=None, edgecolor=None, paths=None),
                         marker_type=None):
        markers = ax.collections if marker_type is None else marker_type
        # Convert which_markers to appropriate marker objects
        try:
            which_markers = self._convert_to_obj(which_markers, markers)
        except (IndexError, ValueError) as e:
            print(e.args[0])
            return

        # Check if marker paths is defined and if so convert it into appropriate path input
        try:
            marker_symbols = marker_props['paths']
        except KeyError:
            marker_props['paths'] = None
        else:
            if(marker_symbols is None):
                marker_paths = None
            else:
                # Iterate through marker symbols - this method is used as appending an unpacked tuple
                # was causing some problems
                marker_paths = [[] for i in xrange(len(marker_symbols))]
                for mi, ms in enumerate(marker_symbols):
                    # Unpack path tuple of only one element
                    if(isinstance(ms, matplotlib.path.Path)):
                        marker_paths[mi] = ms,
                    else:
                        if(isinstance(ms, matplotlib.markers.MarkerStyle)):
                            MS = ms
                        # Convert to marker object
                        else:
                            MS = matplotlib.markers.MarkerStyle(ms)
                        # Transform marker object into Path object and add to path array
                        marker_paths[mi] = MS.get_path().transformed(MS.get_transform()),
            marker_props['paths'] = marker_paths

        # Convert marker sizes to nested list as the property setter takes a list input
        try:
            marker_sizes = marker_props['sizes']
        except KeyError:
            marker_props['sizes'] = None
        else:
            marker_props['sizes'] = [marker_sizes] if(type(marker_sizes) is list) else [[marker_sizes]]
        # Set marker properties
        if(which_markers is not None):
            self._set_props(ax, which_markers, **marker_props)
        else:
            warnings.warn("Trying to get marker properties but which_markers is None")

    def get_marker_props(self, ax, which_markers, marker_type):
        markers = ax.collections if marker_type is None else marker_type
        # Convert which_markers to appropriate marker objects
        try:
            which_markers = self._convert_to_obj(which_markers, markers)
        except (IndexError, ValueError) as e:
            print(e.args[0])
            return

        if(which_markers is not None):
            # Make blank copy of markers_dict that doesn't persist
            markers_dict = copy.deepcopy(self.markers_dict)
            markers_dict = self._get_props(ax, which_markers, markers_dict)
            # Hack to flatten sizes and paths from a nested list/tuple
            warnings.warn("Hack to flatten marker sizes is being used. Can it be improved?")
            markers_dict['sizes'] = [s[0] for s in markers_dict['sizes']]
            markers_dict['paths'] = [p[0] for p in markers_dict['paths']]
            return markers_dict

    def set_text_props(self, ax, which_texts,
                       text_props=dict(fontsize=None, color=None, fontname=None),
                       text_type=None):
        '''
        Set properties of texts added to plot
        '''
        texts = ax.texts if text_type is None else text_type
        # Convert which_texts into appropriate text objects
        try:
            which_texts = self._convert_to_obj(which_texts, texts)
        except (IndexError, ValueError) as e:
            print(e.args[0])
            return

        # Check if there's mathtext if user requests a custom font as it will change font for
        # all mathtext in the plot as it's an rcParam
        if('fontname' in text_props):
            self._check_mathtext(ax, text_props['fontname'])

        # Set text properties
        if(which_texts is not None):
            self._set_props(ax, which_texts, **text_props)
        else:
            warnings.warn("Trying to get text properties but which_texts is None")

    def get_text_props(self, ax, which_texts, text_type=None):
        texts = ax.texts if text_type is None else text_type
        # Convert which_texts into appropriate text objects
        try:
            which_texts = self._convert_to_obj(which_texts, texts)
        except (IndexError, ValueError) as e:
            print(e.args[0])
            return

        if(which_texts is not None):
            # Make blank copy of lines_dict that doesn't persist
            texts_dict = copy.deepcopy(self.texts_dict)
            texts_dict = self._get_props(ax, which_texts, texts_dict)
            return texts_dict
        else:
            warnings.warn("Trying to get text properties but which_texts is None")

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

    def set_log_scale(self, ax, which_axes, set_exp_notation=True, set_log_labels=True):
        # Only accept 'x', 'y' or 'both' for which_labels and get appropriate array from axis dictionary
        try:
            # eval is used as dictionary stores axis objects as string names
            which_axes = eval(self.axis_dict[which_axes], {}, {'ax':ax})
        except KeyError:
            print("Unrecognised value.\n"
                  "Only %s are accepted." % ', '.join(str(t) for t in self.axis_dict))
            return
        for ax_dir in which_axes:
            # Check if axis scale is logarithmic or all tick labels are scientific notation
            # because in these cases we can assume exponential notation will be good
            if(ax_dir.get_scale() == 'log' or all(['e' in str(t) for t in ax_dir.get_majorticklocs()])):
                # Change exponentials notation to log notation - i.e. 10^2, 10^3 -> 2, 3
                ax_dir.set_major_formatter(FuncFormatter(exp_to_log))
                # Add log to label text if it's absent
                self._append_log_text(ax_dir)

# Font related functions -----------------------------------------------

    @staticmethod
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

    @staticmethod
    def set_mathtext_font(font):
        if(font in ['stixsans', 'stix', 'cm']):
            matplotlib.rcParams['mathtext.fontset'] = font
        else:
            matplotlib.rcParams['mathtext.fontset'] = 'custom'
            matplotlib.rcParams['mathtext.rm'] = font
            matplotlib.rcParams['mathtext.it'] = '%s:italic' % font
            matplotlib.rcParams['mathtext.bf'] = '%s:bold' % font

    @staticmethod
    def get_mathtext_font():
        return matplotlib.rcParams['mathtext.fontset']

    def reset_mathtext_font(self):
        self.set_mathtext_font(self.default_mathtext)

# Private functions ------------------------------------------------------------

    def _set_pars(self, num_cols):
        '''
        Set parameters dependent on number of columns requested
        '''
        self.line_width = 1.25 + ((num_cols - 1) * 0.5)
        self.marker_size = 30 + ((num_cols - 1) * 20)
        self.spine_width = self.line_width
        self.label_size = 20 + ((num_cols - 1) * 6)
        self.ticklabel_size = 14 + ((num_cols - 1) * 4)
        self.texts_size = 18 + ((num_cols - 1) * 4)
        self.legendtext_size = 16 + ((num_cols - 1) * 4)

    def _set_mnras_pars(self):
        '''
        Override some default rcParams
        '''
        rcParams = matplotlib.rcParams
        # rcParams are updated after everything plotted on figure
        # so rcParams that override plotting (e.g. prop_cycle)
        # need to be assigned before figure object created
        rcParams['axes.unicode_minus'] = False  # use smaller minus sign in plots
        rcParams['axes.formatter.use_mathtext'] = True  # use mathtext for scientific notation
        rcParams['figure.dpi'] = 300

    def _get_aspect_val(self, aspect):
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

    def _get_figure_size(self, num_cols, aspect_val):
        '''
        Set size of Figure object based on one or two column request
        '''
        # one column or two columns + middle space
        fig_width = 3.333 if num_cols == 1 else 7.639
        fig_height = fig_width * 1./aspect_val
        # Return figure size of double width and height to increase resolution
        return fig_width * 2, fig_height * 2

    def _append_log_text(self, ax_dir):
        label_text = ax_dir.get_label_text()
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

            ax_dir.set_label_text(label_text)

    def _check_mathtext(self, ax, fontname):
        # Check for math text anywhere in the axis object children as custom fonts won't work in this case
        for t in [t.get_text() for t in ax.texts] + [ax.get_xlabel(), ax.get_ylabel()]:
            if('$' in t and fontname is not None):
                warnings.warn("Text contains '$' so mathtext font has been custom updated to specified font. "
                              "This will change the appearance of all mathtext.\n"
                              "If you do not want this change run reset_mathtext_font() to revert back to default, "
                              "do not use a custom font, or remove all of the mathtext.")
                self.set_mathtext_font(fontname)

    def _set_props(self, ax, obj, **kwargs):
        '''
        Sets artist = property for each kwarg
        :param ax: Axes object
        :param obj: Object to apply property changes to
        :param kwargs: Properties to set
        :return: None
        '''
        obj_len = len(obj)
        kwargs = self._remove_empty_keys(kwargs)
        # Convert properties to lists, map lists to length of obj list
        kwargs = {k: self._map_array(self._convert_to_list(v), obj_len) for k,v in kwargs.items()}
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

    def _map_array(self, array, map_len):
        '''
        :param array: Array to map
        :param map_len: Length to map array to
        :return: None
        '''
        if not (map_len % len(array) == 0):
            warnings.warn("Mapping array of non-multiple length (%d -> %d)"
                          % (len(array), map_len), UserWarning)
        return array * (map_len // len(array)) + array[:map_len % len(array)]

    def _remove_empty_keys(self, dict):
        # Remove keys with None values
        # Note this won't catch lists of None but this has to be special and silly input from the user
        return {k: v for k,v in dict.items() if v is not None}
