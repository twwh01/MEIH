#!/usr/bin/env python3
"""
Figure 2: palaeo-latitudinal distribution of well-supported MEIH deposits
T. Wong Hearing
19 June 2026

This script generates main paper Figure 2. 
It uses the rotated data created by ``meih_rotate_deposits.py`` (``data/processed/meih_deposits_rotated.csv``).

Figure 2 plots only deposits with ``deposit_score_WH02 > 2`` and ``likely_interval == "MEIH"``
are shown. Four panels:
    (A) map, PALEOMAP        (B) palaeolatitude histogram, PALEOMAP
    (C) map, MERDITH2021     (D) palaeolatitude histogram, MERDITH2021

Maps are Eckert IV projections with 600 Ma reconstructed coastlines. 
"""

# --- load libraries  -----------------------------------------------------------------------------
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")               # headless figure generation | use 'TkAgg' for interactive use
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import cartopy.crs as ccrs
from gplately import PlateModelManager, PlateReconstruction, PlotTopologies

sys.path.insert(0, str(Path(__file__).resolve().parent))
from meih_rotate_deposits import MODELS_DIR, ROTATION_AGE, OUTPUT_CSV  # noqa: E402
from utils.meih_plot import (
    SIZE_SCORE, ALPHA_SCORE, ICE_LINE_LAT, ICE_LINE_COLOUR,
    score_key, score_rgba, score_shape, add_ice_lines,
)

# --- paths and parameters -----------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]
FIG_DIR = ROOT / "figures"
ROTATED_CSV = OUTPUT_CSV

# column suffix, gplately model name, display label
MODELS = [("PAL", "paleomap", "PALEOMAP"), ("M21", "merdith2021", "MERDITH2021")]
SCORE_THRESHOLD = 2    # keep deposits with score strictly greater than threshold
LAT_BINS = np.arange(-90, 91, 10)
DEPOSIT_FILL = "darkorange"
MAP_CRS = ccrs.EckertIV(central_longitude=0)
DATA_CRS = ccrs.PlateCarree()

# --- functions ----------------------------------------------------------------------------------
## --- load and filter deposits ------------------------------------------------------------------
def load_fig2_deposits() -> pd.DataFrame:
    df = pd.read_csv(ROTATED_CSV)
    sub = df[(df["likely_interval"] == "MEIH")
             & (df["deposit_score_WH02"] > SCORE_THRESHOLD)].copy()
    sub["score_key"] = sub["deposit_score_WH02"].map(score_key)
    return sub

## --- cartopy coastlines and topologies ---------------------------------------------------------
def make_plot_topologies(model_name: str, time: float) -> PlotTopologies:
    model = PlateModelManager().get_model(model_name, data_dir=str(MODELS_DIR))
    try:
        topo = model.get_topology_features()
    except Exception:
        topo = None    # in case the model has no topologies
    recon = PlateReconstruction(
        model.get_rotation_model(),
        topology_features=topo,
        static_polygons=model.get_static_polygons(),
    )
    return PlotTopologies(recon, coastlines=model.get_coastlines(), time=time)

## --- plotting maps -----------------------------------------------------------------------------
def plot_map(ax, gplot, sub, suffix, label):
    ax.set_global()
    # ocean
    ax.patch.set_facecolor("steelblue")
    ax.patch.set_alpha(0.30)
    # continents
    gplot.plot_coastlines(ax, facecolor="#088080", edgecolor="grey",
                          alpha=0.6, linewidth=0.3)
    # axis grid
    ax.gridlines(color="grey", linestyle=":", linewidth=0.4,
                 xlocs=range(-180, 181, 60), ylocs=range(-90, 91, 30))
    # Phanerozoic +/-40 deg ice lines
    for lat in (ICE_LINE_LAT, -ICE_LINE_LAT):
        ax.plot([-180, 180], [lat, lat], transform=DATA_CRS,
                color=ICE_LINE_COLOUR, linestyle="--", linewidth=1.2)
    ax.text(0, 55, "Phanerozoic\n+/-40 deg ice lines", transform=DATA_CRS,
            ha="center", va="center", color=ICE_LINE_COLOUR, fontsize=8,
            bbox=dict(boxstyle="round", fc="white", ec="none", alpha=0.6))
    # deposits: constant orange fill; size/alpha by score
    for key, grp in sub.groupby("score_key"):
        ax.scatter(grp[f"plon_{suffix}"], grp[f"plat_{suffix}"],
                   transform=DATA_CRS, marker=score_shape(key),  # per-score shape (was all "D")
                   s=SIZE_SCORE[key] * 40, facecolor=DEPOSIT_FILL,
                   edgecolor="black", linewidth=0.6,
                   alpha=ALPHA_SCORE[key], zorder=5)
    ax.set_title(label, loc="left", fontweight="bold", fontsize=10)

## --- plotting histograms -----------------------------------------------------------------------
def plot_hist(ax, sub, suffix, label):
    # descending so the highest score stacks at the base of each bar
    keys = sorted(sub["score_key"].unique(), key=int, reverse=True)
    data = [sub.loc[sub["score_key"] == k, f"plat_{suffix}"].to_numpy()
            for k in keys]
    colours = [score_rgba(k, use_alpha=False) for k in keys]
    ax.hist(data, bins=LAT_BINS, orientation="horizontal", stacked=True,
            color=colours, edgecolor="white", linewidth=0.3,
            label=[f"{k}" for k in keys])
    add_ice_lines(ax, axis="y")
    ax.set_ylim(-90, 90)
    ax.set_yticks(np.arange(-90, 91, 30))
    ax.yaxis.set_label_position("right")
    ax.yaxis.tick_right()
    ax.set_ylabel("Palaeolatitude (°N; bin = 10°)", rotation=270, labelpad=15)
    ax.set_xlabel("count")
    ax.set_title(label, loc="left", fontweight="bold", fontsize=10)
    h, lab = ax.get_legend_handles_labels()      # keep legend ascending
    ax.legend(h[::-1], lab[::-1], title="Deposit\nscore", fontsize=8,
              title_fontproperties={"size":10, "weight":"bold"}, loc="upper right", frameon=True)

## --- legend for deposit score (shape & size) ---------------------------------------------------
def size_legend(ax, scores=("3", "4")):
    handles = [
        mlines.Line2D([], [],
                      marker=score_shape(s), linestyle="none",
                      markerfacecolor=DEPOSIT_FILL, markeredgecolor="black",
                      markersize=np.sqrt(SIZE_SCORE[s] * 40), label=f"{s}")
        for s in scores
    ]
    # top-right corner for EckertIV projection; 
    # anchor legend top to y=1 level with the "(A)" title; 
    # horizontal layout to minimise pane overlap
    ax.legend(handles=handles, title="Deposit score", loc="upper right",
              bbox_to_anchor=(1.0, 1.0), ncol=len(scores),
              fontsize=8, title_fontproperties={"size": 10, "weight": "bold"},
              columnspacing=1.5, handletextpad=0.6, borderpad=0.8, frameon=True)

## --- main --------------------------------------------------------------------------------------
def main():
    sub = load_fig2_deposits()
    print(f"Fig 2: {len(sub)} MEIH deposits with score > {SCORE_THRESHOLD}")

    fig = plt.figure(figsize=(12, 9), dpi=450)
    gs = fig.add_gridspec(2, 2, width_ratios=[2, 1], hspace=0.35, wspace=0.18)
    panels = [("A", 0), ("C", 1)]   # row index per model

    pairs = []
    for (suffix, model_name, model_label), (map_letter, row) in zip(MODELS, panels):
        print(f"  [{model_name}] reconstructing coastlines at {ROTATION_AGE} Ma ...")
        gplot = make_plot_topologies(model_name, ROTATION_AGE)
        ax_map = fig.add_subplot(gs[row, 0], projection=MAP_CRS)
        hist_letter = "B" if map_letter == "A" else "D"
        ax_hist = fig.add_subplot(gs[row, 1])
        plot_map(ax_map, gplot, sub, suffix, f"({map_letter})  {model_label}")
        plot_hist(ax_hist, sub, suffix, f"({hist_letter})  {model_label}")
        if map_letter == "A":
            size_legend(ax_map)
        pairs.append((ax_map, ax_hist))

    # draw once so cartopy applies the EckertIV aspect and the map bbox is final
    # then match each histogram's vertical extent to its map 
    fig.canvas.draw()
    for ax_map, ax_hist in pairs:
        bb_map, bb_hist = ax_map.get_position(), ax_hist.get_position()
        ax_hist.set_position([bb_hist.x0, bb_map.y0, bb_hist.width, bb_map.height])

    FIG_DIR.mkdir(parents=True, exist_ok=True)
    out = FIG_DIR / "fig_2_deposits_map_histogram_gt2.png"
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    print(f"saved {out}")
    plt.close(fig)

# --- run ----------------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
