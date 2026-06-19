#!/usr/bin/env python3
"""
Figure 4: GRISLI ice sheet configuration at the South Pole
T. Wong Hearing & A. Pohl
19 June 2026

This script generates main paper Figure 4. 
It uses the rotated data created by ``meih_rotate_deposits.py`` (``data/processed/meih_deposits_rotated.csv``), and
the FOAM sea ice fraction data in directory ``Data_S3_FOAM_files``, and 
the GRISLI ice sheet data in directory ``Data_S5_GRISLI_files``. 

Produces a four-panel plot of maps in South Polar stereographic projection showing the extent of the icesheet after 
304 kyr (end of run) for each of four pCO2 levels, with three- and four-star MEIH deposits overlain. 
"""
# --- load libraries -----------------------------------------------------------------------------
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import matplotlib.lines as mlines
import cartopy.crs as ccrs
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.ticker as mticker
from netCDF4 import Dataset
import numpy as np
import pandas as pd
import os
import warnings
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from pathlib import Path

from utils.meih_plot import score_shape

# --- paths and parameters -----------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"

TIMESTEP_KYR = 304  # kyrs since start of GRISLI run; 304 kyr is final state
do_colorbars = True
outpaths = [str(ROOT / "figures") + os.sep]

## --- input data --------------------------------------------------------------------------------
# per CO2 level (x PAL): (FOAM coupler file, GRISLI ice-sheet file)
FOAM_DIR = DATA_DIR / "Data_S3_FOAM_files"
GRISLI_DIR = DATA_DIR / "Data_S5_GRISLI_files"
RUNS = {
    6:  ('600sc_mob_1680ppm_T41_coupl.nc', '600orX06_rect.nc'),
    8:  ('600sc_mob_2240ppm_T41_coupl.nc', '600orX08_rect.nc'),
    12: ('600sc_mob_3360ppm_T41_coupl.nc', '600orX12_rect.nc'),
    16: ('600sc_mob_4480ppm_T41_coupl.nc', '600orX16_rect.nc'),
}

## --- graphics options --------------------------------------------------------------------------
# headless figure generation (was 'TkAgg' for interactive use)
mpl.use('Agg')
# ignore future warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# total figure size (w x h, mm)
# tuning fonts and markers by figure width and height 
FIG_W_MM, FIG_H_MM = 160, 178
canvas_scale = (FIG_W_MM / 25.4) / 12.0
plot_font_size = 45 * canvas_scale
MARKER_AREA = 100 * canvas_scale ** 2      # scatter marker area per unit score
# greyscale fill by deposit score (shared by the map markers and the legend)
SCORE_COLOURS = {3: '#9e9e9e', 4: 'white'}
projdata = ccrs.SouthPolarStereo()
cmap1 = LinearSegmentedColormap.from_list("my_colormap", ((0.22,0.22,0.56),(0.38,0.49,0.99),(0.51,0.99,1),(0.01,0.51,0),(0.7,0.7,0)), N=256, gamma=1.0)

astr = 'ABCDE'

# --- functions ----------------------------------------------------------------------------------
## --- add circular boundary to polar stereographic axes -----------------------------------------
# see https://stackoverflow.com/questions/73364801/when-using-cartopy-python-to-make-orthographic-plot-how-to-crop-the-map-set
def add_circle_boundary(ax):
    # Compute a circle in axes coordinates, which we can use as a boundary
    # for the map. We can pan/zoom as much as we like - the boundary will be
    # permanently circular.
    theta = np.linspace(0, 2*np.pi, 100)
    center, radius = [0.5, 0.5], 0.5
    verts = np.vstack([np.sin(theta), np.cos(theta)]).T
    circle = mpath.Path(verts * radius + center)
    ax.set_boundary(circle, transform=ax.transAxes)

## --- compute edges of gridded data for pcolormesh ----------------------------------------------
def do_edges(in_lon, in_lat):
    res_x = in_lon[1]-in_lon[0]
    lon_edges = in_lon-res_x/2.
    lon_edges = np.append( lon_edges, lon_edges[-1,]+res_x )
    res_y = in_lat[1]-in_lat[0]
    lat_edges = in_lat-res_y/2.
    lat_edges = np.append( lat_edges, lat_edges[-1,]+res_y )
    return(lon_edges, lat_edges)

# --- load data ----------------------------------------------------------------------------------
# get deposit data (rotated palaeocoordinates from meih_rotate_deposits.py)
occs = pd.read_csv(DATA_DIR / "processed" / "meih_deposits_rotated.csv")

# keep only MEIH deposits with score > 2 (same selection as Fig 2)
occs_meih_gt2 = occs[(occs['likely_interval'] == 'MEIH')
                     & (occs['deposit_score_WH02'] > 2)].copy()
# scores as integers for the marker-size legend
occs_meih_gt2 = occs_meih_gt2.astype({'deposit_score_WH02': 'int'})

# topo-bathy is identical for all panels -> load once
# the TOPO/LAT/LON variable names are specific to this file
topo_file = DATA_DIR / "Data_S3_FOAM_files" / "600_v23238d_128x128_readable.nc"
with Dataset(topo_file) as t:
    topo = t.variables['TOPO'][:]
    latt = t.variables['LAT'][:]
    lont = t.variables['LON'][:]
lont_edges, latt_edges = do_edges(lont, latt)

# --- make figure --------------------------------------------------------------------------------
fig = plt.figure(figsize=(FIG_W_MM / 25.4, FIG_H_MM / 25.4))

for i, (pal_co2, (cpl_name, grisli_name)) in enumerate(RUNS.items()):
    # annual-mean sea-ice fraction from the FOAM coupler
    with Dataset(FOAM_DIR / cpl_name) as cpl:
        frac_an = np.ma.mean(cpl.variables['FRAC'][:], axis=0)
        lat = cpl.variables['lat'][:]
        lon = cpl.variables['lon'][:]

    # GRISLI ice thickness
    with Dataset(GRISLI_DIR / grisli_name) as grisli:
        isdat = grisli.variables['H'][:]
        latis = grisli.variables['lat'][:]
        lonis = grisli.variables['lon'][:]

    isdat_nosmallvalues = np.ma.masked_where(isdat < 1.01, isdat)
    frac_shallow = np.ma.masked_where(topo >= (-100), frac_an)

    # make plot
    ax = plt.subplot(2, 2, i + 1, projection=projdata)
    # plot topo-bathy
    cst = plt.pcolormesh(lont_edges,latt_edges,topo,vmin=-3500,vmax=3500,cmap=cmap1,alpha=1,transform=ccrs.PlateCarree(), rasterized=True)
    plt.contour(lont,latt,topo,[0.],colors='dimgrey',linewidths=2,alpha=1, transform=ccrs.PlateCarree())

    # plot GRISLI ice thickness
    csis = plt.contourf(lonis,latis,isdat_nosmallvalues[TIMESTEP_KYR,:,:],np.arange(0,5200+1.E-9,100),cmap=plt.get_cmap('afmhot'),zorder=5, transform=ccrs.PlateCarree(), rasterized=True)
    plt.contour(lonis,latis,isdat_nosmallvalues[TIMESTEP_KYR,:,:],np.arange(500,8000,500),colors='k',linewidths=0.25,zorder=6, transform=ccrs.PlateCarree())

    # plot mean annual sea ice fraction 50 %
    plt.contour(lon,lat,frac_shallow,[0.5],colors='white',linewidths=5,zorder=7, transform=ccrs.PlateCarree())

    # add lithology occurrences: scatter() takes a single marker, so plot one
    # group per score to give each score its own shape
    for score, grp in occs_meih_gt2.groupby('deposit_score_WH02'):
        plt.scatter(
            grp.plon_PAL,
            grp.plat_PAL,
            marker=score_shape(score),
            s=score * MARKER_AREA,
            edgecolors='black',
            facecolors=SCORE_COLOURS[score],
            alpha=0.8,
            transform=ccrs.PlateCarree(),
            zorder=8
        )

    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=False, linewidth=1, color='k', alpha=1, linestyle='--', zorder=8)
    gl.xlines = True
    gl.xlocator = mticker.FixedLocator([])
    gl.xformatter = LONGITUDE_FORMATTER
    gl.ylocator = mticker.FixedLocator([-75, -60, -45, -30])
    gl.yformatter = LATITUDE_FORMATTER
    ax.set_extent([-180, 180, -90, -35], crs=ccrs.PlateCarree())
    add_circle_boundary(ax)

    plt.annotate('75°S', xy=(0.38, 0.38), xycoords='axes fraction', fontsize=plot_font_size * 0.40, color='k', zorder=9)
    plt.annotate('60°S', xy=(0.28, 0.28), xycoords='axes fraction', fontsize=plot_font_size * 0.40, color='k', zorder=9)
    plt.annotate('45°S', xy=(0.18, 0.18), xycoords='axes fraction', fontsize=plot_font_size * 0.40, color='k', zorder=9)
    plt.annotate(f'({astr[i]})', xy=(0.01, 0.95), xycoords='axes fraction', fontsize=plot_font_size, color='k', zorder=9)
    # pal_co2 value (upper right, same baseline/level as the (A)-(D) labels)
    plt.annotate(f'{pal_co2} PAL', xy=(1.02, 0.95), xycoords='axes fraction', ha='right', fontsize=plot_font_size*0.8, color='k', zorder=9, annotation_clip=False)

fig.subplots_adjust(left=0.003, bottom=0.2, right=0.997, top=0.97, wspace=0.3, hspace=0.1)

## --- add colour bars and legends----------------------------------------------------------------
# colour bars from the last panel's topo-bathy and ice-thickness mappables
if do_colorbars:
    cbar_ax = fig.add_axes([0.1, 0.12, 0.6, 0.0275]) # list [x0, y0, width, height]
    cbar_ax2 = fig.add_axes([0.1, 0.035, 0.6, 0.0275]) # list [x0, y0, width, height]
    cb = plt.colorbar(cst,cax = cbar_ax,orientation='horizontal', ticks=np.arange(-3000,3000+1E-9,1500))
    cb.ax.tick_params(labelsize=plot_font_size*0.4)
    cb.ax.set_title('Topography-bathymetry (m a.s.l.)', weight='normal', fontsize=plot_font_size*0.5)
    cb2 = plt.colorbar(csis,cax = cbar_ax2,orientation='horizontal', ticks=np.arange(0,5000+1E-9,1000))
    cb2.ax.tick_params(labelsize=plot_font_size*0.4)
    cb2.ax.set_title("Ice thickness (m)", weight="normal", fontsize=plot_font_size*0.5)

# single deposit-score legend for all panels, bottom-right beside the colour bars
# score 3 = grey, score 4 = white; markers match the map deposits
score_handles = [
    mlines.Line2D([], [], marker=score_shape(s), linestyle='none',
                  markerfacecolor=fc, markeredgecolor='black',
                  markersize=np.sqrt(s * MARKER_AREA), label=f'{s}')
    for s, fc in SCORE_COLOURS.items()
]
fig.legend(handles=score_handles, title='Deposit\nscore',
           loc='center', bbox_to_anchor=(0.86, 0.085),
           fontsize=plot_font_size * 0.4, title_fontsize=plot_font_size * 0.45,
           labelspacing=2.0, handletextpad=1.6, borderpad=1.0, frameon=False)

## --- save figure -------------------------------------------------------------------------------
for outpath in outpaths:
    outname = f"{outpath}fig_4_GRISLI_panel_plot.png"

    if os.path.isfile(outname):
        os.remove(outname)

    plt.savefig(outname, format="png", dpi=600)
    print(f"Saving to file: {outname}")

plt.close('all')
