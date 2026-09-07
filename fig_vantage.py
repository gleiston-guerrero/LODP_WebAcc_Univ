# -*- coding: utf-8 -*-
"""Figura 4 (fig_vantage.pdf) generada a partir de los doce JSON multipunto.
Regla: consolidacion por mayoria sobre las tres pasadas de cada punto de
observacion; se omiten los proveedores presentes en menos de cuatro sitios
segun se observa desde Ecuador (n = 121 sitios)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

OUT, IN, GREY = "#9E3D00", "#1F3B73", "#3A3A3A"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8.5,
                     "axes.edgecolor": GREY, "axes.linewidth": 0.9,
                     "pdf.fonttype": 42, "savefig.bbox": "tight",
                     "savefig.pad_inches": 0.03})
N = 121
# vendor: (Ecuador, United States, United Kingdom, Germany)
DATA = [
    ("Google Analytics and Ads",   71, 69, 65, 63),
    ("YouTube and DoubleClick",    37, 35, 31, 21),
    ("Meta",                       24, 24, 19, 15),
    ("Microsoft",                  14, 14,  0,  0),
    ("LinkedIn Insight Tag",       14, 14,  7,  3),
    ("TikTok",                     13, 13, 10,  8),
    ("Hotjar",                      9,  9,  8,  6),
    ("Siteimprove",                 7,  7,  6,  6),
    ("PixelYourSite/Sourcebuster",  7,  6,  7,  7),
    ("X and Twitter",               5,  5,  4,  4),
    ("Adobe and Tealium",           4,  4,  4,  4),
    ("TapAd",                       4,  4,  0,  0),
    ("Baidu",                       4,  4,  2,  0),
]
labels = [d[0] for d in DATA]
vals = np.array([[d[1], d[2], d[3], d[4]] for d in DATA], float) / N * 100
y = np.arange(len(DATA))[::-1]
h = 0.20
fig, ax = plt.subplots(figsize=(7.0, 5.4))
series = [("Ecuador", OUT, "///"), ("United States", OUT, ""),
          ("United Kingdom", IN, "\\\\\\"), ("Germany", IN, "")]
for j, (nm, col, hat) in enumerate(series):
    ax.barh(y + (1.5 - j) * h, vals[:, j], height=h, color=col, hatch=hat,
            edgecolor="white", linewidth=0.6)
ax.set_yticks(y); ax.set_yticklabels(labels)
ax.set_xlabel("Sites setting at least one cookie before consent (\\%)".replace("\\", ""))
ax.set_xlim(0, 62)
ax.grid(axis="x", color="#CCCCCC", linewidth=0.6); ax.set_axisbelow(True)
for s in ("top", "right"): ax.spines[s].set_visible(False)
ax.legend(handles=[Patch(facecolor=c, hatch=ht, edgecolor="white", label=nm)
                   for nm, c, ht in series],
          loc="lower right", ncol=1, frameon=False)
fig.savefig("fig_vantage.pdf")
print("fig_vantage.pdf generada desde los datos reales")
