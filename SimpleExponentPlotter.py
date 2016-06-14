import numpy as np
import matplotlib.pyplot as plt
from pyblish import make_figure, pyblishify

fig, ax = make_figure(1, 1)

x = np.arange(0, 1, 0.01)
y1 = 1-np.exp(-x)
y2 = 1-np.exp(-x**0.5)

ax.scatter(x, y1, label='1')
ax.scatter(x, y2, label='2')

ax.set_xlabel('x')
ax.set_ylabel('y')

ax.legend(loc='upper right')

pyblishify(fig, 1, 'square', 'all', 'all', ['left', 'bottom'], None, 'all', None, 'all', None,
           save_file='C:\\Users\\MarcE\\Desktop\\pyblish\\standard.png')

plt.show()
