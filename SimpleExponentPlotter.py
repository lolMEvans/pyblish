from cycler import cycler
import numpy as np
import matplotlib.pyplot as plt
import pyblish
from pyblish import pyblishify

fig = plt.figure()
ax = fig.add_subplot(111)

w = 0.01
nmin, nmax = (7.94E14, 7.94E19)
n0 = nmax


n = np.logspace(np.log10(nmin), np.log10(nmax), 20)
for exp in [0.01, 0.1]:
    y = (n/n0)**exp
    ax.scatter(n, y, s = 5, linestyle= '--', label = '$\mathrm{w = %f}$' % exp)
    ax.plot(n, y, label = '$\mathrm{w = %f}$' % exp)

# Shrink current axis by 20%
box = ax.get_position()
#ax.set_position([box.x0, box.y0, box.width * 0.5, box.height])
l = ax.legend(loc = 'upper center', ncol = 5, columnspacing = 0.6, handlelength = 1.0, handletextpad = 0.4,
              bbox_to_anchor=(0.5, 0.75), frameon = False)

ax.set_xscale('log')
ax.set_yscale('log')

ax.plot((nmax, nmax), (ax.get_ylim()[0], ax.get_ylim()[1]), ls = '--', c = 'gray')
ax.text(0.8, 0.1, '$\mathrm{n = n_0}$', transform = ax.transAxes)
ax.text(0.8, 0.2, 'LOL', transform = ax.transAxes)

ax.set_xlabel('LOL') # ('$\mathit{log\ n\ [cm^{-3}]}$')
ax.set_ylabel('LOL') # '$\mathrm{(n/n_0)^w}$')


pyblishify(fig, 1, 'square', which_lines=-1, which_markers='all', change_log_scales=False)
pyblish.set_spine_props(ax, 'bottom', {'linewidth': 3.0, 'color': (0, 0, 1, 0.5)}, True)

pyblish.set_line_props(ax, '2,0', {'color': ['blue', 'green'], 'linestyle': ['-', '--']})
# line_props = pyblish.get_line_props(ax, '2,0')
#
# # Order in correct way! - make into own function in pyblish? Methinks so.
# # pass in objs_name (e.g. spines) - auto knows order should be in
# line_props_new = {k: [] for k in line_props[0].keys()}
# for k, v in line_props.items():
#     for j, vv in v.items():
#         line_props_new[j].append(vv)
# print(line_props_new)
# print(pyblish.get_props_from_nested_dict(line_props, 'line', range(0, len(line_props))))
# line_props_new['color'] = ['green', 'red', 'purple']
#pyblish.set_line_props(ax, 'all', line_props_new)


plt.tight_layout()
# plt.savefig('/localhome/py09mge/test.png', bbox_extra_artists=(l,), bbox_inches='tight')
plt.show()
# plt.close()



def trim(seq):
    trimmed_range = []
    seen = set()
    for i in seq:
        if(i not in seen):
            seen.add(i)
            trimmed_range.append(i)
    return trimmed_range