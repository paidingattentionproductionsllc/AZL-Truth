#!/usr/bin/env python3
"""Generate PWA icons for AZL Universe Explorer."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

def make_icon(size):
    path = f'icon-{size}.png'
    fig, ax = plt.subplots(figsize=(1, 1), dpi=size)
    fig.patch.set_facecolor('#000008')
    ax.set_facecolor('#000008')
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.set_aspect('equal')
    ax.axis('off')

    rng = np.random.default_rng(42)
    xs, ys = rng.uniform(-1, 1, 600), rng.uniform(-1, 1, 600)
    mask = xs**2 + ys**2 < 0.98
    xm, ym = xs[mask], ys[mask]
    for xi, yi in zip(xm, ym):
        ax.plot(xi, yi, '.', color='white',
                markersize=rng.uniform(0.3, 1.8),
                alpha=float(rng.uniform(0.15, 0.9)), zorder=1)

    for r, a in [(0.87, 0.15), (0.70, 0.30), (0.52, 0.50), (0.33, 0.72)]:
        ring = plt.Circle((0, 0), r, fill=False, color='#00ffff',
                           linewidth=max(0.8, size / 250), alpha=a)
        ax.add_patch(ring)

    ax.add_patch(plt.Circle((0, 0), 0.22, color='#001a2a', zorder=3))
    ax.add_patch(plt.Circle((0, 0), 0.11, color='#00cccc', zorder=4))
    ax.add_patch(plt.Circle((0, 0), 0.05, color='white', zorder=5))

    fig.savefig(path, dpi=size, facecolor='#000008',
                bbox_inches='tight', pad_inches=0)
    plt.close(fig)
    print(f'[icon] generated {path}')

if __name__ == '__main__':
    for s in [192, 512]:
        make_icon(s)
