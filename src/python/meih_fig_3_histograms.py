#!/usr/bin/env python3
"""
Figure 3: palaeolatitude histograms of candidate deposits
T. Wong Hearing
19 June 2026

This script generates main paper Figure 3. 
It uses the rotated data created by ``meih_rotate_deposits.py`` (``data/processed/meih_deposits_rotated.csv``).

Produces a grid of histograms of deposit palaeolatitude, faceted by ``likely_interval`` (rows: MEIH, Ediacaran) 
and rotation model (columns: PALEOMAP, MERDITH2021), coloured by ``deposit_score_WH02``. 
Each panel overlays the Phanerozoic +/-40 deg ice band. 
Optionally (turned off for the main paper figure) each panel overlays the area-by-latitude reference curve 
(relative surface area of each 10 deg latitude band). 
"""
# --- load libraries  -----------------------------------------------------------------------------
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")               # headless figure generation | use 'TkAgg' for interactive use
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

sys.path.insert(0, str(Path(__file__).resolve().parent))
from meih_rotate_deposits import OUTPUT_CSV 
from utils.meih_plot import ( 
    score_key, score_rgba, add_ice_lines, latitude_area_curve,
)

# --- paths and parameters -----------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]
FIG_DIR = ROOT / "figures"
ROTATED_CSV = OUTPUT_CSV

INTERVALS = ["MEIH", "Ediacaran"]                       # rows
MODELS = [("PAL", "PALEOMAP"), ("M21", "MERDITH2021")]  # columns
BIN_WIDTH = 10
LAT_BINS = np.arange(-90, 91, BIN_WIDTH)

LATITUDE_AREA_CURVE = False  # overlay the area-by-latitude reference curve on each panel

# --- functions ----------------------------------------------------------------------------------
## --- load and filter deposits ------------------------------------------------------------------
def load_deposits() -> pd.DataFrame:
    df = pd.read_csv(ROTATED_CSV)
    # missing scores are treated as 0
    df["score_key"] = df["deposit_score_WH02"].fillna(0).map(score_key)
    return df

## --- panel plotting ----------------------------------------------------------------------------
### --- peak panel count -------------------------------------------------------------------------
def panel_peak(sub, suffix):
    """
    Count in the tallest latitude bin of a panel (0 if empty).
    """
    plats = sub[f"plat_{suffix}"].dropna().to_numpy()
    return int(np.histogram(plats, bins=LAT_BINS)[0].max()) if plats.size else 0

### --- plot single panel ------------------------------------------------------------------------
def plot_panel(ax, sub, suffix):
    # descending so the highest score stacks at the bottom of each bar
    keys = sorted(sub["score_key"].unique(), key=int, reverse=True)
    data = [sub.loc[sub["score_key"] == k, f"plat_{suffix}"].to_numpy() for k in keys]
    colours = [score_rgba(k, use_alpha=False) for k in keys]
    add_ice_lines(ax, axis="x")
    if any(len(d) for d in data):
        ax.hist(data, bins=LAT_BINS, stacked=True, color=colours, edgecolor="white", linewidth=0.3)
    ax.set_xlim(-90, 90)
    ax.set_xticks(np.arange(-90, 91, 30))
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))   # integer counts

    if LATITUDE_AREA_CURVE:
        # overlay the area-by-latitude reference curve, scaled to the tallest bin in this panel
        peak = panel_peak(sub, suffix)
        if peak > 0:
            lat_upper, area_scaled = latitude_area_curve(BIN_WIDTH)
            curve = area_scaled / area_scaled.max() * peak
            ax.plot(lat_upper, curve, color="black", linewidth=1.0, zorder=6)

## --- main --------------------------------------------------------------------------------------
def main():
    df = load_deposits()
    counts = {iv: int((df["likely_interval"] == iv).sum()) for iv in INTERVALS}
    print(f"Fig 3: deposits per interval {counts}")

    fig, axes = plt.subplots(
        len(INTERVALS), len(MODELS), figsize=(9, 5.5), dpi=300,
        sharex=True, sharey=True,
    )

    # common count axis for every panel: tallest bin across all panels (+0.5 headroom)
    global_peak = max(panel_peak(df[df["likely_interval"] == iv], sfx)
                      for iv in INTERVALS for sfx, _ in MODELS)
    y_top = global_peak + 0.5

    for r, interval in enumerate(INTERVALS):
        for c, (suffix, model_label) in enumerate(MODELS):
            ax = axes[r, c]
            sub = df[df["likely_interval"] == interval]
            plot_panel(ax, sub, suffix)
            ax.set_ylim(0, y_top)
            if r == 0:
                ax.set_title(model_label, fontweight="bold", fontsize=10)
            if c == 0:
                ax.set_ylabel(f"{interval}\ncount")
            if r == len(INTERVALS) - 1:
                ax.set_xlabel(
                    f"Palaeolatitude (°N; bin = {BIN_WIDTH}°; rotation 600 Ma)"
                )

    # shared score legend
    present = sorted(df["score_key"].unique(), key=int)
    handles = [plt.Rectangle((0, 0), 1, 1, facecolor=score_rgba(k, use_alpha=False),
                             edgecolor="white") for k in present]
    # anchor the legend to the right of the panels
    fig.legend(handles, [f"{k}" for k in present], title="Deposit\nscore",
               loc="center left", bbox_to_anchor=(0.9, 0.5), fontsize=8,
               title_fontproperties={"size": 10, "weight": "bold"}, frameon=True)

    fig.tight_layout(rect=(0, 0, 0.89, 1))
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    out = FIG_DIR / "fig_3_lat_hist_score_interval.png"
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    print(f"saved {out}")
    plt.close(fig)

# --- run ----------------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
