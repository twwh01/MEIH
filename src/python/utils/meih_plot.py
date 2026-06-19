"""Shared plotting helpers for the MEIH deposit figures (Figs 2 & 3).

Defines the score-driven aesthetics (size / alpha / colour) used to render
candidate glacial deposits, and small helpers for the Phanerozoic +/-40 deg
"ice line" annotation and the area-by-latitude reference curve.

The colour ramp is R's ``viridis::mako(n = 6, end = 0.8, direction = -1)``
(low score = light teal, high score = dark), sampled exactly from seaborn's
mako colormap (which shares viridisLite's data).
"""

from __future__ import annotations

import numpy as np
from matplotlib.colors import to_rgba

# --- score-driven aesthetics (keys are stringified integer scores) -------
SIZE_SCORE = {
    "NA": 0.25, "0": 0.25, "1": 0.5, "2": 1.0, "3": 2.0, "4": 4.0, "5": 8.0,
}
ALPHA_SCORE = {
    "NA": 1 / 6, "0": 1 / 6, "1": 2 / 6, "2": 3 / 6, "3": 4 / 6, "4": 5 / 6, "5": 1.0,
}
SHAPE_SCORE = {
    "NA": ".", "0": ".", "1": ".", "2": ".", "3": "o", "4": "D", "5": "*",
}
# mako(end=0.8) reversed: score 0 = light teal ... score 5 = near-black
COLOUR_SCORE = {
    "NA": "#7f7f7f",
    "0": "#60ceac",
    "1": "#36a2ab",
    "2": "#3574a1",
    "3": "#414488",
    "4": "#312142",
    "5": "#0b0405",
}

ICE_LINE_LAT = 40.0          # Phanerozoic +/-40 deg ice line
ICE_LINE_COLOUR = "darkorange"
ICE_BAND_COLOUR = "steelblue"


def score_key(value) -> str:
    """Map a numeric deposit score (possibly NaN) to a palette key string."""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "NA"
    return str(int(round(float(value))))


def score_rgba(key: str, *, use_alpha: bool = True):
    """RGBA tuple for a score, optionally folding ``ALPHA_SCORE`` into alpha."""
    alpha = ALPHA_SCORE.get(key, 1.0) if use_alpha else 1.0
    return to_rgba(COLOUR_SCORE.get(key, "#7f7f7f"), alpha)


def score_shape(value) -> str:
    """Marker shape for a deposit score.

    Accepts a numeric score (e.g. ``3``), a NaN/None, or an already-stringified
    key (e.g. ``"3"``); resolves it via ``score_key`` so callers can pass an
    integer score directly.
    """
    return SHAPE_SCORE.get(score_key(value), ".")


def add_ice_lines(ax, axis: str = "x", *, label: bool = True) -> None:
    """Shade the |lat| > 40 deg ice zones and draw dashed +/-40 deg lines.

    ``axis`` is the axis that carries latitude ("x" for vertical histograms /
    Fig 3, "y" for the horizontal histograms in Fig 2).
    """
    lo, hi = -ICE_LINE_LAT, ICE_LINE_LAT
    if axis == "x":
        ax.axvspan(-90, lo, color=ICE_BAND_COLOUR, alpha=0.10, lw=0, zorder=0)
        ax.axvspan(hi, 90, color=ICE_BAND_COLOUR, alpha=0.10, lw=0, zorder=0)
        ax.axvline(lo, ls="--", color=ICE_BAND_COLOUR, lw=1, zorder=1)
        ax.axvline(hi, ls="--", color=ICE_BAND_COLOUR, lw=1, zorder=1)
    else:
        ax.axhspan(-90, lo, color=ICE_BAND_COLOUR, alpha=0.10, lw=0, zorder=0)
        ax.axhspan(hi, 90, color=ICE_BAND_COLOUR, alpha=0.10, lw=0, zorder=0)
        ax.axhline(lo, ls="--", color=ICE_BAND_COLOUR, lw=1, zorder=1)
        ax.axhline(hi, ls="--", color=ICE_BAND_COLOUR, lw=1, zorder=1)


def latitude_area_curve(bin_width: float = 10.0, earth_radius: float = 6371.0):
    """Reference curve: relative surface area of each latitude band.

    Mirrors the R Fig 3 calculation: band area = 2*pi*R^2*(sin(lat2)-sin(lat1)),
    z-scored then shifted/scaled to span ~[0, 1]. Returns ``(lat_upper, scaled)``.
    """
    lat_1 = np.arange(-90, 90, bin_width)
    lat_2 = lat_1 + bin_width
    area = 2 * np.pi * earth_radius**2 * (
        np.sin(np.deg2rad(lat_2)) - np.sin(np.deg2rad(lat_1))
    )
    z = (area - area.mean()) / area.std(ddof=1)
    scaled = (z + np.abs(z.min())) / z.max()
    return lat_2, scaled
