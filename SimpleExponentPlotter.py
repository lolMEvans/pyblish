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
    ax.scatter(n, y, s=5, linestyle='--', label='$\mathrm{w = %f}$' % exp)
    p1, = ax.plot(n, y, label='$\mathrm{w = %f}$' % exp)

# Shrink current axis by 20%
box = ax.get_position()
# ax.set_position([box.x0, box.y0, box.width * 0.5, box.height])
l = plt.legend(handles=[p1], loc='upper center', ncol=5, columnspacing=0.6, handlelength=1.0, handletextpad=0.4,
               bbox_to_anchor=(0.5, 0.75), frameon=False)
lol = plt.gca().add_artist(l)
x = plt.legend(loc='upper center', ncol=5, columnspacing=0.6, handlelength=1.0, handletextpad=0.4,
               bbox_to_anchor=(0.5, 0.25), frameon=False)
# Add another legend!

# ax.set_xscale('log')
# ax.set_yticks([0.1, 0.5, 1.0, 1.5, 2.0])
# ax.set_yscale('log')

ax.plot((nmax, nmax), (ax.get_ylim()[0], ax.get_ylim()[1]), ls = '--', c = 'gray')
ax.text(0.8, 0.1, '$\mathrm{n = n_0}$', transform=ax.transAxes)
ax.text(0.8, 0.2, 'LOL', transform=ax.transAxes)

ax.set_xlabel('$\mathit{\mathbf{L_O^L}}\ \mathrm{L_O^L}$') # ('$\mathit{log\ n\ [cm^{-3}]}$')
ax.set_ylabel('Lmao') # '$\mathrm{(n/n_0)^w}$')


pyblishify(fig, 1, 'square', which_lines=-1, which_markers='all', which_log_scales='all',
           line_props={'color': ['blue', 'red', 'green']})
# pyblish.set_font(pyblish.get_default('font_mathtext'), True)

plt.tight_layout()
# plt.savefig('/localhome/py09mge/test.png', bbox_extra_artists=(l,), bbox_inches='tight')
plt.show()
# plt.close()