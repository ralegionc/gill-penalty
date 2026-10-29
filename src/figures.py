"""Posters.

figures/where_gills_can_live.png  the hero: temperature excess against body mass, with the
                                  plain-gill ceiling and the exchanger contours
figures/heat_outruns_oxygen.png   blood temperature and oxygen along one gill lamella
figures/breakeven.png             heat lost breathing per joule burned, gills against lungs
figures/gilled_whale.png          FishBase gill areas carried up to a blue whale
"""
import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle

import physics as ph
from common import AIR, BAD, BG, DERIVED, FIGURES, GRID, HEAT, PALE, RESULTS, SUBTLE, TEXT, WATER

plt.rcParams.update({"font.family": "DejaVu Sans", "axes.edgecolor": BG, "savefig.facecolor": BG})
CAP_LO, CAP_HI = 0.04, 0.25          # shark to seal-grade blood, mL O2 per mL
CAP_REF = 0.20                       # mammal-grade blood for the exchanger contours


def glow(ax, x, y, color, lw=2.0, z=3, **kw):
    for w, a in ((lw * 5, 0.06), (lw * 2.6, 0.14), (lw, 1.0)):
        ax.plot(x, y, color=color, lw=w, alpha=a, solid_capstyle="round", zorder=z, **kw)


def dot(ax, x, y, color, s=60, z=5, hollow=False):
    for k, a in ((9, 0.05), (4, 0.12), (1.8, 0.25)):
        ax.scatter(x, y, s=s * k, color=color, alpha=a, lw=0, zorder=z)
    if hollow:
        ax.scatter(x, y, s=s, facecolor=BG, edgecolor=color, lw=1.6, zorder=z + 1)
    else:
        ax.scatter(x, y, s=s, color=color, lw=0, zorder=z + 1)


def frame(fig, title, dek, foot):
    fig.patch.set_facecolor(BG)
    fig.text(0.035, 0.945, title, color=TEXT, fontsize=30, weight="bold", va="top")
    fig.text(0.035, 0.885, dek, color=SUBTLE, fontsize=13.5, va="top")
    fig.text(0.035, 0.02, foot, color="#5f6570", fontsize=8.5, va="bottom", linespacing=1.6, wrap=True)


def axstyle(ax):
    ax.set_facecolor(BG)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.tick_params(colors=SUBTLE, labelsize=10, length=0)
    ax.grid(color=GRID, lw=0.6, zorder=0)


# --- hero ---------------------------------------------------------------------------------

LABEL_POS = {  # (dx points, dy points, ha) for the labels in the hero
    "Atlantic bluefin tuna": (14, 4, "left"), "Salmon shark": (-12, -2, "right"),
    "Swordfish": (-12, 0, "right"), "Opah": (12, 0, "left"), "Skipjack tuna (lab)": (12, 4, "left"),
    "Basking shark": (12, 2, "left"), "Leatherback turtle": (12, -6, "left"),
    "Weddell seal": (12, 2, "left"), "Emperor penguin": (12, 4, "left"), "Sea otter": (-12, 0, "right"),
    "Harbour porpoise": (12, 0, "left"), "Bottlenose dolphin": (-6, -16, "right"),
    "Bowhead whale": (-12, 4, "right"), "Blue whale": (-12, -4, "right"),
}


def hero():
    ex = pd.read_csv(RESULTS / "animals.csv")
    fig = plt.figure(figsize=(20, 12.3), dpi=100)
    frame(fig, "Where Gills Can Live",
          "How far above the water temperature an animal can keep any part of its body, by how it breathes",
          "Ceiling: 19.6 J per mL O2 burned x blood O2 capacity (0.04 to 0.25 mL/mL) / 3.7 J per mL per K, full extraction. "
          "Exchanger contours for blood carrying 0.20 mL/mL.\n"
          "Fish: Carey and Lawson 1973; Carey 1982; Neill et al. 1976; Goldman et al. 2004; Wegner et al. 2015; Dolton et al. 2023. "
          "Turtle: Frair et al. 1972. Mammals and penguin: typical core against habitat water (illustrative).")
    ax = fig.add_axes([0.075, 0.1, 0.66, 0.74])
    axstyle(ax)
    ax.set_xscale("log")
    ax.set_yscale("log")
    xl = (0.3, 4e5)
    ax.set_xlim(*xl)
    ax.set_ylim(0.05, 60)

    # the plain-gill zone: below the ceiling for any blood
    lo, hi = ph.ceiling(CAP_LO), ph.ceiling(CAP_HI)
    ax.axhspan(0.05, lo, color=WATER, alpha=0.17, lw=0, zorder=1)
    for k in range(30):  # fade from the shark-blood ceiling up to the richest blood
        y0, y1 = lo * (hi / lo) ** (k / 30), lo * (hi / lo) ** ((k + 1) / 30)
        ax.axhspan(y0, y1, color=WATER, alpha=0.17 * (1 - k / 30), lw=0, zorder=1)
    glow(ax, xl, [hi, hi], WATER, lw=1.6, z=2)
    ax.plot(xl, [lo, lo], color=WATER, lw=0.8, alpha=0.5, zorder=2)
    ax.text(0.36, hi * 1.12, f"plain-gill ceiling: {hi:.1f} K for the richest blood", color=WATER, fontsize=11.5, va="bottom")
    ax.text(0.36, lo * 1.08, f"{lo:.1f} K for shark blood", color=WATER, fontsize=10, alpha=0.7, va="bottom")
    ax.text(0.36, 0.1, "about 25,000 fish species live down here,\nat the temperature of the water",
            color=WATER, fontsize=11, alpha=0.75, va="center")

    # exchanger contours
    for eff, ls in ((0.9, (0, (6, 4))), (0.95, (0, (3, 3))), (0.97, (0, (1, 3)))):
        y = ph.excess_with_rete(CAP_REF, eff)
        ax.plot(xl, [y, y], color=HEAT, lw=1.1, ls=ls, alpha=0.65, zorder=2)
        ax.text(0.36, y * 1.05, f"gills plus a heat exchanger {eff:.0%} effective",
                color=HEAT, fontsize=10, alpha=0.85, ha="left", va="bottom")

    styles = {"fish_rete": (HEAT, False), "fish_unknown": (HEAT, True), "air": (AIR, False)}
    for _, r in ex.iterrows():
        col, hollow = styles[r.group]
        if r.scope == "blood":
            col = WATER
        y = r.excess_k
        if pd.notna(r.excess_lo_k):
            top = r.excess_hi_k if pd.notna(r.excess_hi_k) else y
            ax.plot([r.mass_kg] * 2, [r.excess_lo_k, top], color=col, lw=2.2, alpha=0.45, zorder=4,
                    solid_capstyle="round")
        dot(ax, r.mass_kg, y, col, s=70, hollow=hollow)
        dx, dy, ha = LABEL_POS.get(r.animal, (10, 0, "left"))
        name = r.animal.replace(" (lab)", "")
        lab = f"{name}, {r.tissue}" if r.group != "air" else name
        if r.scope == "blood":
            lab, dx, dy = "skipjack blood on its way to the gills", 10, -8
        ax.annotate(lab, (r.mass_kg, y), xytext=(dx, dy), textcoords="offset points", ha=ha,
                    va="center", color=col if r.group != "air" else PALE, fontsize=10.5)
    ax.annotate("?", (4000, 1.25), xytext=(-16, 0), textcoords="offset points", color=HEAT, fontsize=15,
                weight="bold", va="center", ha="center")

    ax.set_xlabel("body mass, kg", color=SUBTLE, fontsize=11.5)
    ax.set_ylabel("tissue temperature above the water, K (log)", color=SUBTLE, fontsize=11.5)
    ax.set_yticks([0.1, 0.3, 1, 3, 10, 30])
    ax.set_yticklabels(["0.1", "0.3", "1", "3", "10", "30"])
    ax.set_xticks([1, 10, 100, 1e3, 1e4, 1e5])
    ax.set_xticklabels(["1", "10", "100", "1,000", "10,000", "100,000"])

    # side panel
    w = json.loads((RESULTS / "gilled_whale.json").read_text())
    side = fig.add_axes([0.765, 0.1, 0.21, 0.74])
    side.axis("off")
    blocks = [
        (TEXT, 15, "bold", "The ceiling"),
        (SUBTLE, 11.5, "normal",
         "Blood cools to water temperature in the gills, then\ncarries at most its own oxygen into the body.\n"
         "Burning that oxygen can warm it by about 1 K.\nNo body size or burst of effort changes that."),
        (TEXT, 15, "bold", "The way out"),
        (SUBTLE, 11.5, "normal",
         "A counter-current exchanger hands heat from\noutgoing to incoming blood before it reaches\n"
         "the gills. All 30-odd warm fish have one.\nBluefin muscle implies 95%; the opah's whole\nbody, 89%."),
        (TEXT, 15, "bold", "A blue whale with gills"),
        (SUBTLE, 11.5, "normal",
         f"{w['excess_k']:.0f} K above 10 C water is {w['plain_penalty']:.0f} times the ceiling.\n"
         f"Plain gills would shed {w['plain_gill_heat_loss_mw']:.1f} MW against the\n"
         f"{w['fmr_kw']:.0f} kW it burns. To break even its whole\ncirculation needs an exchanger "
         f"{w['rete_breakeven']:.0%} effective,\n{w['rete_half']:.0%} to leave half its heat for the skin."),
        (TEXT, 15, "bold", "The open question"),
        (SUBTLE, 11.5, "normal",
         "Basking sharks keep white muscle 1.0 to 1.5 K\nwarm: three to five times the ceiling for shark\n"
         "blood. The physics says they hide an exchanger,\nor carry heat down from warmer water."),
    ]
    y = 1.0
    for col, size, weight, txt in blocks:
        side.text(0, y, txt, color=col, fontsize=size, weight=weight, va="top", transform=side.transAxes,
                  linespacing=1.45)
        y -= 0.045 if weight == "bold" else 0.03 * (txt.count("\n") + 1) + 0.045
    fig.savefig(FIGURES / "where_gills_can_live.png")
    plt.close(fig)


# --- mechanism ----------------------------------------------------------------------------

def mechanism():
    ratio = ph.heat_vs_oxygen(0.10)
    x, o2, heat = ph.lamella(2.0, ratio, n=20000)
    fig = plt.figure(figsize=(16, 9), dpi=100)
    frame(fig, "Heat Outruns Oxygen",
          "Blood crossing one gill lamella: how close it gets to the water's temperature, and to its oxygen",
          f"Effective diffusivities: heat in blood {ph.K_TISSUE / (ph.C_BLOOD * 1e6):.1e} m2/s; oxygen "
          f"{ph.D_O2 * ph.ALPHA_O2 / ph.blood_o2_capacitance(0.10):.1e} m2/s for blood carrying 0.10 mL O2 per mL "
          f"over a 9 kPa loading span. Ratio {ratio:,.0f}. Oxygen loading set to reach 86% at the exit.")
    ax = fig.add_axes([0.07, 0.12, 0.6, 0.66])
    axstyle(ax)
    glow(ax, x, heat, HEAT, lw=2.4)
    glow(ax, x, o2, WATER, lw=2.4)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.04)
    ax.set_xlabel("distance along the lamella (entry to exit)", color=SUBTLE, fontsize=11.5)
    ax.set_ylabel("share of the way to the water's state", color=SUBTLE, fontsize=11.5)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1])
    ax.set_yticklabels(["0", "25%", "50%", "75%", "100%"])
    ax.text(0.05, 1.0, "heat: gone almost at the entrance", color=HEAT, fontsize=12.5, va="bottom")
    ax.text(0.55, 0.55, "oxygen: loaded slowly,\nall the way along", color=WATER, fontsize=12.5)

    ins = fig.add_axes([0.72, 0.38, 0.25, 0.4])
    axstyle(ins)
    n = int(0.003 * len(x))
    glow(ins, x[:n] * 100, heat[:n], HEAT, lw=2)
    glow(ins, x[:n] * 100, o2[:n], WATER, lw=2)
    ins.set_xlim(0, 0.3)
    ins.set_ylim(0, 1.04)
    ins.set_title("first 0.3% of the lamella", color=TEXT, fontsize=12, loc="left")
    ins.set_xlabel("% of length", color=SUBTLE, fontsize=10)
    fig.text(0.72, 0.29, f"Heat equilibrates about {ratio:,.0f} times more readily\nthan oxygen. "
             "Any gill good enough to load\noxygen has already cooled the blood to\nthe water by the time it does.",
             color=SUBTLE, fontsize=11.5, va="top", linespacing=1.5)
    fig.savefig(FIGURES / "heat_outruns_oxygen.png")
    plt.close(fig)


# --- breakeven ----------------------------------------------------------------------------

def breakeven():
    w = json.loads((RESULTS / "gilled_whale.json").read_text())
    dt = np.logspace(-1.3, np.log10(45), 300)
    fig = plt.figure(figsize=(16, 10), dpi=100)
    frame(fig, "The Breakeven Line",
          "Heat thrown away by breathing, for every joule of food burned, against how warm the body runs",
          "Gills: excess x (1 - exchanger effectiveness) / ceiling, blood 0.20 mL O2/mL (band 0.04 to 0.25 for no exchanger). "
          "Lungs: inhaled air at the water's temperature, 90% humid, exhaled saturated at 37 C; 0.04 to 0.08 mL O2 taken per mL of air.")
    ax = fig.add_axes([0.08, 0.1, 0.88, 0.72])
    axstyle(ax)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(0.05, 45)
    ax.set_ylim(3e-3, 300)
    ax.add_patch(Rectangle((0.05, 1), 45, 300, color=BAD, alpha=0.10, lw=0, zorder=1))
    glow(ax, [0.05, 45], [1, 1], BAD, lw=1.2, z=2)
    ax.text(0.06, 1.15, "breakeven: above this line, burning more food to stay warm loses more heat than it makes",
            color=BAD, fontsize=11.5, va="bottom")
    ax.fill_between(dt, ph.gill_penalty(dt, CAP_HI), ph.gill_penalty(dt, CAP_LO), color=WATER, alpha=0.12, lw=0)
    glow(ax, dt, ph.gill_penalty(dt, CAP_REF), WATER, lw=2.2)
    ax.text(0.07, ph.gill_penalty(0.07, CAP_REF) * 2.2, "plain gills", color=WATER, fontsize=12.5)
    for eff, ls in ((0.9, (0, (6, 4))), (0.97, (0, (3, 3))), (0.99, (0, (1, 3)))):
        ax.plot(dt, ph.gill_penalty(dt, CAP_REF, eff), color=HEAT, lw=1.4, ls=ls, alpha=0.8, zorder=3)
        ax.text(44, ph.gill_penalty(44, CAP_REF, eff) * 1.12, f"gills + exchanger {eff:.0%}", color=HEAT,
                fontsize=10.5, ha="right", va="bottom")
    t_air = 37 - dt
    lung_lo, lung_hi = ph.lung_penalty(37, t_air, 0.08), ph.lung_penalty(37, t_air, 0.04)
    ax.fill_between(dt, lung_lo, lung_hi, color=AIR, alpha=0.15, lw=0)
    glow(ax, dt, np.sqrt(lung_lo * lung_hi), AIR, lw=2.2)
    ax.text(0.07, lung_hi[0] * 1.5, "lungs (mostly the cost of humidifying air, not warming it)", color=AIR, fontsize=12.5)

    dot(ax, w["excess_k"], w["plain_penalty"], WATER, s=90)
    ax.annotate(f"blue whale with gills: {w['plain_penalty']:.0f}x", (w["excess_k"], w["plain_penalty"]),
                xytext=(-12, 10), textcoords="offset points", ha="right", color=TEXT, fontsize=12)
    dot(ax, w["excess_k"], w["lung_penalty"], AIR, s=90)
    ax.annotate(f"the same whale with lungs: {w['lung_penalty']:.2f}", (w["excess_k"], w["lung_penalty"]),
                xytext=(-12, -14), textcoords="offset points", ha="right", color=TEXT, fontsize=12)
    ax.set_xlabel("body temperature above the water, K", color=SUBTLE, fontsize=11.5)
    ax.set_ylabel("heat lost through breathing per joule burned", color=SUBTLE, fontsize=11.5)
    ax.set_xticks([0.1, 0.3, 1, 3, 10, 30])
    ax.set_xticklabels(["0.1", "0.3", "1", "3", "10", "30"])
    ax.set_yticks([0.01, 0.1, 1, 10, 100])
    ax.set_yticklabels(["0.01", "0.1", "1", "10", "100"])
    fig.savefig(FIGURES / "breakeven.png")
    plt.close(fig)


# --- whale gills --------------------------------------------------------------------------

def gilled_whale():
    g = pd.read_csv(DERIVED / "gill_points.csv")
    g = g[~g.air]
    w = json.loads((RESULTS / "gilled_whale.json").read_text())
    m_kg = g.mass_g / 1000
    a_m2 = g.area_cm2 / 1e4
    b, a = np.polyfit(np.log10(m_kg), np.log10(a_m2), 1)
    tb, ta = np.polyfit(np.log10(m_kg[g.tuna]), np.log10(a_m2[g.tuna]), 1)
    fig = plt.figure(figsize=(16, 10), dpi=100)
    frame(fig, "Gills for a Blue Whale",
          f"Total gill area of {g.sci.nunique()} water-breathing fish species, carried up to a 100-tonne body",
          "FishBase GILLAREA (v25.04, 'doubtful' rows dropped). Requirement: Kleiber basal x 2.5, divided by the highest "
          "oxygen uptake per m2 of gill in FishBase OXYGEN at active metabolism (white sucker, 5,300 mg/m2/h at 20 C). "
          "Skin: 0.1 x mass^(2/3) m2.")
    ax = fig.add_axes([0.08, 0.1, 0.6, 0.72])
    axstyle(ax)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(1e-5, 3e5)
    ax.set_ylim(1e-6, 3e5)
    xs = np.logspace(-5, np.log10(2e5), 50)
    other = ~g.tuna
    ax.scatter(m_kg[other], a_m2[other], s=16, color=WATER, alpha=0.55, lw=0, zorder=3)
    dot(ax, m_kg[g.tuna], a_m2[g.tuna], HEAT, s=22)
    ax.plot(xs, 10 ** (a + b * np.log10(xs)), color=WATER, lw=1.2, ls=(0, (4, 4)), alpha=0.7)
    ax.plot(xs, 10 ** (ta + tb * np.log10(xs)), color=HEAT, lw=1.2, ls=(0, (4, 4)), alpha=0.7)
    skin = 0.1 * xs ** (2 / 3)
    glow(ax, xs, skin, PALE, lw=1.4, z=2)
    ax.text(3e-5, 0.1 * 3e-5 ** (2 / 3) * 2.2, "skin", color=PALE, fontsize=11.5)
    ax.text(3e2, 10 ** (a + b * np.log10(3e2)) * 0.3, f"fish gills, slope {b:.2f}", color=WATER, fontsize=11.5,
            ha="left", va="top")
    ax.text(0.02, 10 ** (ta + tb * np.log10(0.02)) * 1.6, f"tunas, slope {tb:.2f}", color=HEAT, fontsize=11.5,
            ha="right", va="bottom")
    tuna_ratio = (a_m2[g.tuna] / (0.1 * m_kg[g.tuna] ** (2 / 3)))
    m = w["mass_kg"]
    dot(ax, m, w["gill_area_m2"], TEXT, s=110)
    ax.annotate(f"needed: {w['gill_area_m2']:,.0f} m2", (m, w["gill_area_m2"]), xytext=(-14, 12),
                textcoords="offset points", ha="right", color=TEXT, fontsize=12.5)
    dot(ax, m, w["skin_area_m2"], PALE, s=70)
    ax.annotate(f"its skin: {w['skin_area_m2']:,.0f} m2", (m, w["skin_area_m2"]), xytext=(-14, -14),
                textcoords="offset points", ha="right", color=PALE, fontsize=12)
    ax.set_xlabel("body mass, kg", color=SUBTLE, fontsize=11.5)
    ax.set_ylabel("area, m2", color=SUBTLE, fontsize=11.5)

    side = fig.add_axes([0.72, 0.1, 0.26, 0.72])
    side.axis("off")
    lines = [
        ("Size is not the problem.", TEXT, 15, "bold"),
        (f"{w['gill_area_m2']:,.0f} m2 of gill is about {w['gill_area_m2'] / w['skin_area_m2']:.0f} times the\n"
         f"whale's skin; the tunas here carry {tuna_ratio.min():.0f} to\n{tuna_ratio.max():.0f} times their skin "
         f"as gill. Pumping {w['water_m3_s']:.2f} m3\nof water a second, {w['water_m3_s'] * 60:.0f} m3 a minute, is the\n"
         "scale a blue whale already engulfs in\na single feeding lunge.", SUBTLE, 12, "normal"),
        ("Heat is.", TEXT, 15, "bold"),
        (f"That much gill would bring the whale's\n{w['blood_l_s']:.0f} L of blood a second to water\n"
         f"temperature and lose {w['plain_gill_heat_loss_mw']:.1f} MW,\n{w['plain_penalty']:.0f} times what it burns.",
         SUBTLE, 12, "normal"),
    ]
    y = 1.0
    for txt, col, size, weight in lines:
        side.text(0, y, txt, color=col, fontsize=size, weight=weight, va="top", transform=side.transAxes,
                  linespacing=1.5)
        y -= 0.06 if weight == "bold" else 0.045 * (txt.count("\n") + 1) + 0.05
    fig.savefig(FIGURES / "gilled_whale.png")
    plt.close(fig)


def main():
    hero()
    mechanism()
    breakeven()
    gilled_whale()


if __name__ == "__main__":
    main()
