#!/usr/bin/env python3
"""
Figure S5: GRISLI ice sheets early in the model run (initial transient) 
# T. Wong Hearing; A. Pohl
# 19 June 2026

Produces the same 2x2 South Polar porjection panels as Fig 4 (6/8/12/16 PAL) for 
GRISLI ice thickness (plus FOAM annual-mean sea-ice 50% contour) for an earlier 
GRISLI timestep defaulting to 10 kyr

This version is comparing simulations only and does not plot the MEIH deposits. 
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

TIMESTEP_KYR = 10  # kyrs since start of GRISLI run; 304 kyr is the final state
do_colorbars = True
outpaths = [str(ROOT / "figures") + os.sep]

# input data per CO2 level (x PAL): (FOAM coupler file, GRISLI ice-sheet file)
FOAM_DIR = DATA_DIR / "Data_S3_FOAM_files"
GRISLI_DIR = DATA_DIR / "Data_S5_GRISLI_files"
RUNS = {
    6:  ('600sc_mob_1680ppm_T41_coupl.nc', '600orX06_rect.nc'),
    8:  ('600sc_mob_2240ppm_T41_coupl.nc', '600orX08_rect.nc'),
    12: ('600sc_mob_3360ppm_T41_coupl.nc', '600orX12_rect.nc'),
    16: ('600sc_mob_4480ppm_T41_coupl.nc', '600orX16_rect.nc'),
}

# ignore future warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# headless figure generation (was 'TkAgg' for interactive use)
mpl.use('Agg')
# graphics options
plot_font_size = 45
projdata = ccrs.SouthPolarStereo()
cmap1 = LinearSegmentedColormap.from_list("my_colormap", ((0.22,0.22,0.56),(0.38,0.49,0.99),(0.51,0.99,1),(0.01,0.51,0),(0.7,0.7,0)), N=256, gamma=1.0)

astr = 'ABCDE'

# --- make plot ----------------------------------------------------------------------------------
# https://stackoverflow.com/questions/73364801/when-using-cartopy-python-to-make-orthographic-plot-how-to-crop-the-map-set
def add_circle_boundary(ax):
    # Compute a circle in axes coordinates, which we can use as a boundary
    # for the map. We can pan/zoom as much as we like - the boundary will be
    # permanently circular.
    theta = np.linspace(0, 2*np.pi, 100)
    center, radius = [0.5, 0.5], 0.5
    verts = np.vstack([np.sin(theta), np.cos(theta)]).T
    circle = mpath.Path(verts * radius + center)
    ax.set_boundary(circle, transform=ax.transAxes)

def do_edges(in_lon, in_lat):
    res_x = in_lon[1]-in_lon[0]
    lon_edges = in_lon-res_x/2.
    lon_edges = np.append( lon_edges, lon_edges[-1,]+res_x )
    res_y = in_lat[1]-in_lat[0]
    lat_edges = in_lat-res_y/2.
    lat_edges = np.append( lat_edges, lat_edges[-1,]+res_y )
    return(lon_edges, lat_edges)

# topo-bathy is identical for all panels -> load once
# TOPO/LAT/LON variable names are specific to this file
topo_file = DATA_DIR / "Data_S3_FOAM_files" / "600_v23238d_128x128_readable.nc"
with Dataset(topo_file) as t:
    topo = t.variables['TOPO'][:]
    latt = t.variables['LAT'][:]
    lont = t.variables['LON'][:]
lont_edges, latt_edges = do_edges(lont, latt)

fig = plt.figure(figsize=(2*6, 2*7.8))

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

fig.subplots_adjust(left=0.003, bottom=0.2, right=0.997, top=0.97, wspace=0.1, hspace=0.1)

# colour bars from the last panel's topo-bathy and ice-thickness mappables
if do_colorbars:
    cbar_ax = fig.add_axes([0.1, 0.12, 0.8, 0.0275]) # list [x0, y0, width, height]
    cbar_ax2 = fig.add_axes([0.1, 0.035, 0.8, 0.0275]) # list [x0, y0, width, height]
    cb = plt.colorbar(cst,cax = cbar_ax,orientation='horizontal', ticks=np.arange(-3000,3000+1E-9,1500))
    cb.ax.tick_params(labelsize=plot_font_size*0.4)
    cb.ax.set_title('Topography-bathymetry (m a.s.l.)', weight='normal', fontsize=plot_font_size*0.5)
    cb2 = plt.colorbar(csis,cax = cbar_ax2,orientation='horizontal', ticks=np.arange(0,5000+1E-9,1000))
    cb2.ax.tick_params(labelsize=plot_font_size*0.4)
    cb2.ax.set_title("Ice thickness (m)", weight="normal", fontsize=plot_font_size*0.5)

# --- save figure --------------------------------------------------------------------------------
for outpath in outpaths:
    outname = f"{outpath}fig_s5_GRISLI_{TIMESTEP_KYR}kyr_panel_plot.png"

    if os.path.isfile(outname):
        os.remove(outname)

    plt.savefig(outname, format="png", dpi=600)
    print(f"Saving to file: {outname}")

plt.close('all')
