#!/usr/bin/env python3
"""
Figures S1 & S2: PALEOMAP palaeogeography basemaps for FOAM, LMDZ, and GRISLI model runs 
T. Wong Hearing & A. Pohl
19 June 2026

This script generates the supplementary figures S1 & S2. 
It uses the topographic basemap file used for the FOAM, LMDZ, and GRISLI runs.
"""
# --- load libraries -----------------------------------------------------------------------------
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import cartopy.crs as ccrs
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.ticker as mticker
from netCDF4 import Dataset
import numpy as np
import os
import warnings
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from pathlib import Path

# --- paths and parameters -----------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
outpaths = [str(ROOT / "figures") + os.sep]

# set up
do_colorbars = True

# ignore future warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# figure generation 
mpl.use('Agg')
# change to 'TkAgg' for interactive use
# graphics options
plot_font_size = 45
cmap1 = LinearSegmentedColormap.from_list("my_colormap", ((0.22,0.22,0.56),(0.38,0.49,0.99),(0.51,0.99,1),(0.01,0.51,0),(0.7,0.7,0)), N=256, gamma=1.0)

# --- define edges for pcolormesh ----------------------------------------------------------------
def do_edges(in_lon, in_lat):
    res_x = in_lon[1]-in_lon[0]
    lon_edges = in_lon-res_x/2.
    lon_edges = np.append( lon_edges, lon_edges[-1,]+res_x )
    res_y = in_lat[1]-in_lat[0]
    lat_edges = in_lat-res_y/2.
    lat_edges = np.append( lat_edges, lat_edges[-1,]+res_y )
    return(lon_edges, lat_edges)

# get topobathy file - same file for all
topo_postslarti_file = DATA_DIR / "Data_S3_FOAM_files" / "600_v23238d_128x128_readable.nc"  # using variable TOPO
t = Dataset(topo_postslarti_file)

# --- figure s1: EckertIV projection paleogeography ----------------------------------------------
projdata = ccrs.EckertIV(central_longitude = 0)

# allows for use of different palaeogeography file resolutions
if topo_postslarti_file.name == '600_v23238d.nc':
    topo = t.variables['600_v23238d'][:]
    latt = t.variables['latitude'][:]
    lont = t.variables['longitude'][:]
elif topo_postslarti_file.name == '600_v23238d_128x128_readable.nc':
    topo = t.variables['TOPO'][:]
    latt = t.variables['LAT'][:]
    lont = t.variables['LON'][:]
t.close()

[lont_edges, latt_edges] = do_edges(lont, latt)

# make plot
fig = plt.figure(
    figsize = (7, 5),
    dpi = 450
)
ax = plt.subplot(projection = projdata)
ax1 = ax.pcolormesh(lont_edges,latt_edges,topo,vmin=-3500,vmax=3500,cmap=cmap1,alpha=1,transform=ccrs.PlateCarree(), rasterized=True)
ax.contour(lont,latt,topo,[0.],colors='dimgrey',linewidths=2,alpha=1, transform=ccrs.PlateCarree())
ax.gridlines(
    color='k',
    linestyle='--',
    xlocs=np.arange(-180,180,60),
    ylocs=np.arange(-90,90,30),
    draw_labels = True
    )
if do_colorbars:
    cbar_ax = fig.add_axes([0.25, 0.05, 0.5, 0.05])  # [l,b,w,h]
    cb = fig.colorbar(ax1, cax=cbar_ax, orientation='horizontal', label='Topography-bathymetry (m a.s.l.)')
    cb.ax.set_title('Topography-bathymetry (m a.s.l.)', weight='normal') #, fontsize=plot_font_size * 0.2)

for outpath in outpaths:
    outname = f'{outpath}fig_s1_FOAM_pgeog_EckertIV.png'

    if os.path.isfile(outname):
        os.remove(outname)

    plt.savefig(outname, format='png', dpi=600)
    print(f'Saving to file: {outname}')
plt.close('all')

# --- figure s2 - south polar projection paleogeography ------------------------------------------
projdata = ccrs.SouthPolarStereo()

# https://stackoverflow.com/questions/73364801/when-using-cartopy-python-to-make-orthographic-plot-how-to-crop-the-map-set
def add_circle_boundary(ax):
    # Compute a circle in axes coordinates, which we can use as a boundary for the map. 
    # We can pan/zoom as much as we like - the boundary will be permanently circular.
    theta = np.linspace(0, 2*np.pi, 100)
    center, radius = [0.5, 0.5], 0.5
    verts = np.vstack([np.sin(theta), np.cos(theta)]).T
    circle = mpath.Path(verts * radius + center)
    ax.set_boundary(circle, transform=ax.transAxes)

# make plot
fig = plt.figure(
    figsize = (5, 5.5),
    dpi = 450
)
ax = plt.subplot(projection = projdata)
ax1 = ax.pcolormesh(lont_edges,latt_edges,topo,vmin=-3500,vmax=3500,cmap=cmap1,alpha=1,transform=ccrs.PlateCarree(), rasterized=True)
ax.contour(lont,latt,topo,[0.],colors='dimgrey',linewidths=2,alpha=1, transform=ccrs.PlateCarree())
gl = ax.gridlines(
    crs=ccrs.PlateCarree(),
    color='k',
    linestyle='--',
    # xlocs=np.arange(-180,180,60),
    # ylocs=np.arange(-90,90,30),
    draw_labels = False
    )
gl.xlines = True
gl.xlocator = mticker.FixedLocator([])
gl.xformatter = LONGITUDE_FORMATTER
gl.ylocator = mticker.FixedLocator([-75, -60, -45, -30])
gl.yformatter = LATITUDE_FORMATTER
ax.set_extent([-180, 180, -90, -35], crs=ccrs.PlateCarree())
add_circle_boundary(ax)

plt.annotate('75°S', xy=(0.38, 0.38), xycoords='axes fraction', fontsize=plot_font_size * 0.30, color='k', zorder=9)
plt.annotate('60°S', xy=(0.28, 0.28), xycoords='axes fraction', fontsize=plot_font_size * 0.30, color='k', zorder=9)
plt.annotate('45°S', xy=(0.18, 0.18), xycoords='axes fraction', fontsize=plot_font_size * 0.30, color='k', zorder=9)

if do_colorbars:
    cbar_ax = fig.add_axes([0.125, 0.05, 0.75, 0.025])  # list [x0, y0, width, height]
    cb = plt.colorbar(ax1, cax=cbar_ax, orientation='horizontal', ticks=np.arange(-3000, 3000 + 1E-9, 1500))
    # cb.ax.tick_params(labelsize=plot_font_size * 0.2)
    cb.ax.set_title('Topography-bathymetry (m a.s.l.)', weight='normal') #, fontsize=plot_font_size * 0.2)

for outpath in outpaths:
    outname = f'{outpath}fig_s2_GRISLI_pgeog_SouthPolar.png'

    if os.path.isfile(outname):
        os.remove(outname)

    plt.savefig(outname, format='png', dpi=600)
    print(f'Saving to file: {outname}')
plt.close('all')
