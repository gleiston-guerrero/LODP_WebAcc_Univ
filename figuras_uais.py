#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figuras accesibles para el manuscrito UAIS.

Cumple las instrucciones a autores de UAIS: patrones ADEMAS del color,
relacion de contraste >= 4.5:1 de cada tinta frente al blanco, tipografia
legible al tamano de impresion y leyenda fuera del area de datos.
Texto interno en ingles (figuras compartidas entre la version EN y la ES).
"""
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

# --- Paleta accesible ------------------------------------------------------
BENCH = "#1F3B73"   # azul marino  ~ 11.4:1 sobre blanco
ECU   = "#9E3D00"   # ocre oscuro  ~  7.3:1 sobre blanco
GREY  = "#3A3A3A"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 8.5,
    "axes.labelsize": 8.5,
    "axes.titlesize": 8.5,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "axes.edgecolor": GREY,
    "axes.linewidth": 0.9,
    "pdf.fonttype": 42,          # fuentes incrustadas como TrueType
    "ps.fonttype": 42,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.03,
})

N = 63


def wilson(k, n, z=1.959963985):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return 100 * max(0.0, c - h), 100 * min(1.0, c + h)


def newcombe(k1, n1, k2, n2, z=1.959963985):
    l1, u1 = [v / 100 for v in wilson(k1, n1, z)]
    l2, u2 = [v / 100 for v in wilson(k2, n2, z)]
    d = k1 / n1 - k2 / n2
    lo = d - z * math.sqrt(l1 * (1 - l1) / n1 + u2 * (1 - u2) / n2)
    hi = d + z * math.sqrt(u1 * (1 - u1) / n1 + l2 * (1 - l2) / n2)
    return 100 * d, 100 * lo, 100 * hi


# ===========================================================================
# Figura 1 — forest plot de diferencias de riesgo con IC del 95 %
# ===========================================================================
BLOCKS = [
    ("Privacy governance", [
        ("Privacy notice published",            59, 39),
        ("Applicable framework cited",          47, 31),
        ("Data-subject rights listed",          47, 35),
        ("Privacy contact or DPO",   54, 24),
    ]),
    ("Pre-consent tracking", [
        ("Tracking cookie before consent",     43, 41),
        ("Any cookie before consent",  56, 55),
        ("Consent banner displayed",            22, 15),
        ("CMP detected", 12, 14),
    ]),
    ("Accessibility", [
        ("Accessibility statement",    47,  7),
        ("No level-A failure detected",         25,  5),
        ("No automatic failure at all",          6,  0),
    ]),
    ("Transport security", [
        ("Valid TLS certificate",               63, 58),
    ]),
]

rows, labels, seps = [], [], []
y = 0
for block, items in BLOCKS:
    seps.append((y, block))
    for lab, kw, ke in items:
        d, lo, hi = newcombe(kw, N, ke, N)
        rows.append((y, d, lo, hi, kw, ke))
        labels.append(lab)
        y -= 1
    y -= 0.7

fig, ax = plt.subplots(figsize=(5.15, 5.3))
ax.axvline(0, color=GREY, lw=1.1, zorder=1)
for (yy, d, lo, hi, kw, ke) in rows:
    sig = lo > 0 or hi < 0
    ax.plot([lo, hi], [yy, yy], color=BENCH, lw=2.0, solid_capstyle="butt", zorder=3)
    ax.plot([lo, lo], [yy - .16, yy + .16], color=BENCH, lw=1.6, zorder=3)
    ax.plot([hi, hi], [yy - .16, yy + .16], color=BENCH, lw=1.6, zorder=3)
    ax.plot([d], [yy], marker="s" if sig else "o", ms=6,
            mfc=BENCH if sig else "white", mec=BENCH, mew=1.8, zorder=4)
    ax.text(99, yy, f"{kw} : {ke}", va="center", ha="right",
            fontsize=7, color=GREY)

ax.set_yticks([r[0] for r in rows])
ax.set_yticklabels(labels)
for yy, block in seps:
    ax.text(-45, yy + 0.75, block, fontsize=8.5, fontweight="bold", color=GREY, va="center")
ax.set_xlim(-46, 100)
ax.set_xticks([-40, -20, 0, 20, 40, 60, 80])
ax.set_ylim(min(r[0] for r in rows) - 0.9, 1.6)
ax.set_xlabel("Risk difference (percentage points)")
ax.xaxis.set_label_coords(0.43, -0.075)
ax.spines[["top", "right", "left"]].set_visible(False)
ax.spines["bottom"].set_bounds(-46, 80)
ax.tick_params(axis="y", length=0)
ax.grid(axis="x", color="#CCCCCC", lw=0.6, zorder=0)
ax.set_axisbelow(True)
leg = [Line2D([], [], marker="s", ls="none", mfc=BENCH, mec=BENCH, ms=6,
              label="95 % CI excludes zero"),
       Line2D([], [], marker="o", ls="none", mfc="white", mec=BENCH, mew=1.6, ms=6,
              label="95 % CI includes zero")]
ax.text(99, 1.45, "Compliant sites (b : e)", va="center", ha="right",
        fontsize=7, style="italic", color=GREY)
ax.legend(handles=leg, loc="lower center", bbox_to_anchor=(0.42, -0.235),
          ncol=2, frameon=False)
fig.savefig("fig_forest.pdf")
plt.close(fig)

# ===========================================================================
# Figura 2 — comportamiento de cookies previo al consentimiento
# ===========================================================================
COOK = [("Any cookie\nbefore consent", 56, 55),
        ("Tracking cookie\nbefore consent",  43, 41),
        ("Consent banner\nshown",            22, 15),
        ("CMP\ndetected",                    12, 14)]

fig, ax = plt.subplots(figsize=(5.15, 3.3))
w = 0.36
xs = range(len(COOK))
for i, (lab, kw, ke) in enumerate(COOK):
    for j, (k, col, hat) in enumerate(((kw, BENCH, "//"), (ke, ECU, "xx"))):
        lo, hi = wilson(k, N)
        p = 100 * k / N
        x = i + (j - 0.5) * w
        ax.bar(x, p, width=w, color="white", edgecolor=col, hatch=hat, lw=1.4, zorder=2)
        ax.errorbar(x, p, yerr=[[p - lo], [hi - p]], fmt="none", ecolor=col,
                    elinewidth=1.5, capsize=4, capthick=1.5, zorder=3)
        ax.text(x, hi + 2.2, f"{p:.1f}", ha="center", fontsize=7.5, color=col)
ax.set_xticks(list(xs))
ax.set_xticklabels([c[0] for c in COOK])
ax.set_ylabel("Percentage of sites (95 % Wilson CI)")
ax.set_ylim(0, 108)
ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="y", color="#CCCCCC", lw=0.6, zorder=0)
ax.set_axisbelow(True)
leg = [Patch(facecolor="white", edgecolor=BENCH, hatch="//", label=f"Benchmark group (n={N})"),
       Patch(facecolor="white", edgecolor=ECU, hatch="xx", label=f"Ecuador (n={N})")]
ax.legend(handles=leg, loc="lower center", bbox_to_anchor=(0.5, -0.34), ncol=2, frameon=False)
fig.savefig("fig_cookies.pdf")
plt.close(fig)

# ===========================================================================
# Figura 3 — distribucion de nodos con fallo por nivel WCAG (+ sensibilidad)
# ===========================================================================
fig, axes = plt.subplots(1, 2, figsize=(5.15, 3.1))
PANELS = [
    ("(a) All rules enabled\n(WCAG 2.0/2.1 AAA included)",
     ["A", "AA", "AAA"], [19, 22, 60], [45, 29, 26]),
    ("(b) Sensitivity: AAA rules excluded\n(re-normalised to A + AA)",
     ["A", "AA"], [46.3, 53.7], [60.8, 39.2]),
]
for ax, (title, cats, bench, ecu) in zip(axes, PANELS):
    w = 0.36
    for i, c in enumerate(cats):
        for j, (v, col, hat) in enumerate(((bench[i], BENCH, "//"), (ecu[i], ECU, "xx"))):
            x = i + (j - 0.5) * w
            ax.bar(x, v, width=w, color="white", edgecolor=col, hatch=hat, lw=1.4, zorder=2)
            ax.text(x, v + 1.6, f"{v:.0f}" if float(v).is_integer() else f"{v:.1f}",
                    ha="center", fontsize=7.5, color=col)
    ax.set_xticks(range(len(cats)))
    ax.set_xticklabels([f"Level {c}" for c in cats])
    ax.set_ylim(0, 72)
    ax.set_title(title, fontsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#CCCCCC", lw=0.6, zorder=0)
    ax.set_axisbelow(True)
axes[0].set_ylabel("Percentage of the group's failing nodes")
leg = [Patch(facecolor="white", edgecolor=BENCH, hatch="//", label=f"Benchmark group (n={N})"),
       Patch(facecolor="white", edgecolor=ECU, hatch="xx", label=f"Ecuador (n={N})")]
fig.legend(handles=leg, loc="lower center", bbox_to_anchor=(0.5, -0.045), ncol=2, frameon=False)
fig.savefig("fig_wcag_niveles.pdf")
plt.close(fig)

# ===========================================================================
# Figura D1 — composicion del grupo de referencia por pais (sustituye al mapa)
# ===========================================================================
PAISES = [("United States", 24), ("United Kingdom", 7), ("China", 6), ("Australia", 5),
          ("Germany", 3), ("Hong Kong SAR", 3), ("Canada", 3), ("Switzerland", 2),
          ("France", 2), ("Singapore", 2), ("Japan", 2), ("Sweden", 1),
          ("Netherlands", 1), ("Belgium", 1), ("South Korea", 1)]
assert sum(v for _, v in PAISES) == 63, sum(v for _, v in PAISES)
fig, ax = plt.subplots(figsize=(5.0, 3.6))
ys = range(len(PAISES))
ax.barh(list(ys), [v for _, v in PAISES], color="white", edgecolor=BENCH,
        hatch="//", lw=1.3, height=0.68, zorder=2)
for i, (_, v) in enumerate(PAISES):
    ax.text(v + 0.35, i, str(v), va="center", fontsize=8, color=BENCH)
ax.set_yticks(list(ys))
ax.set_yticklabels([p for p, _ in PAISES])
ax.invert_yaxis()
ax.set_xlabel("Number of institutions in the benchmark group (n = 63)")
ax.set_xlim(0, 26)
ax.spines[["top", "right", "left"]].set_visible(False)
ax.tick_params(axis="y", length=0)
ax.grid(axis="x", color="#CCCCCC", lw=0.6, zorder=0)
ax.set_axisbelow(True)
fig.savefig("fig_paises.pdf")
plt.close(fig)

# ===========================================================================
# Figura D2 — cronologia de los regimenes de proteccion de datos (vertical)
# ===========================================================================
LEYES = [(1988, "Australia", "Privacy Act"), (1995, "Hong Kong SAR", "PDPO"),
         (2000, "Canada (federal)", "PIPEDA"), (2003, "Japan", "APPI"),
         (2011, "South Korea", "PIPA"), (2012, "Singapore", "PDPA"),
         (2018, "European Union", "GDPR"), (2018, "United Kingdom", "DPA 2018 / UK GDPR"),
         (2020, "California (US)", "CCPA"), (2021, "China", "PIPL"),
         (2021, "Ecuador", "LOPDP"), (2023, "Switzerland", "revised FADP")]

fig, ax = plt.subplots(figsize=(5.0, 3.9))
n = len(LEYES)
for i, (yr, juris, name) in enumerate(LEYES):
    y = n - i
    is_ec = juris == "Ecuador"
    col = ECU if is_ec else BENCH
    ax.plot([0, 0.6], [y, y], color=col, lw=1.1, zorder=2)
    ax.plot([0], [y], marker="D" if is_ec else "o", ms=7 if is_ec else 5.5,
            mfc=col if is_ec else "white", mec=col, mew=1.7, zorder=3)
    ax.text(0.75, y, f"{juris} \u2014 {name}", va="center", ha="left", fontsize=8.5,
            color=col, fontweight="bold" if is_ec else "normal")
    ax.text(-0.55, y, str(yr), va="center", ha="right", fontsize=8.5, color=col,
            fontweight="bold" if is_ec else "normal")
ax.plot([0, 0], [0.4, n + 0.6], color=GREY, lw=1.2, zorder=1)
ax.set_xlim(-1.9, 8.4)
ax.set_ylim(0.2, n + 1.4)
ax.axis("off")
ax.text(-0.55, n + 0.95, "Year", va="center", ha="right", fontsize=8,
        style="italic", color=GREY)
ax.text(0.75, n + 0.95, "Jurisdiction and instrument", va="center", ha="left",
        fontsize=8, style="italic", color=GREY)
leg = [Line2D([], [], marker="D", ls="none", mfc=ECU, mec=ECU, ms=7, label="Ecuador (case study)"),
       Line2D([], [], marker="o", ls="none", mfc="white", mec=BENCH, mew=1.6, ms=5.5,
              label="Jurisdictions of the benchmark group")]
ax.legend(handles=leg, loc="lower center", bbox_to_anchor=(0.45, -0.09), ncol=2, frameon=False)
fig.savefig("fig_cronologia.pdf")
plt.close(fig)

print("Figuras generadas: fig_forest.pdf, fig_cookies.pdf, fig_wcag_niveles.pdf, "
      "fig_paises.pdf, fig_cronologia.pdf")
