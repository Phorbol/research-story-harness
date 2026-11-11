"""Generate an explicitly synthetic qualitative landscape; no research data."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    axis = np.linspace(-2.2, 2.2, 90)
    x, y = np.meshgrid(axis, axis)
    z = 0.2 * (x*x + y*y) - 1.5 * np.exp(-((x-.7)**2 + (y+.5)**2)) - 0.9 * np.exp(-((x+1.1)**2 + (y-.8)**2) / .5)
    fig = plt.figure(figsize=(5, 3.2), facecolor='white')
    ax = fig.add_subplot(projection='3d')
    ax.plot_surface(x, y, z, cmap='viridis', linewidth=0, antialiased=True)
    ax.view_init(elev=28, azim=-65)
    ax.set_axis_off()
    fig.text(.5, .06, 'Synthetic qualitative landscape', ha='center', fontsize=9, color='#33424a')
    fig.savefig(Path(__file__).with_name('qualitative-landscape.png'), dpi=160, bbox_inches='tight', pad_inches=.05)
    plt.close(fig)


if __name__ == '__main__':
    main()
