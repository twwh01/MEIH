# MEIH: the Mid-Ediacaran IceHouse
Supplementary code and (some of the) data for Wong Hearing et al. (submitted): *A Phanerozoic-style icehouse climate in the middle Ediacaran*. 

Authors: Thomas W. Wong Hearing, Alexandre Pohl, Thomas M. Vandyk, Benjamin H. Tindal, Frédéric Fluteau, Alexander G. Liu, Thomas H. P. Harvey, Mark Williams

Code: Thomas W. Wong Hearing, Alexandre Pohl

This directory contains all the script files necessary for reproducing the analyses and figures in the paper and its supplementary information. 

The NetCDF data files are not included here; they are .gitignore'd out as they are large files. They are available on Zenodo at: . 

To run the code that requires the NetCDF files, download the files from the Zenodo repository and unzip them to the corresponding directories: `data/Data_S3_FOAM_files/`, `data/Data_S4_LMDZ_files/`, and `data/Data_S5_GRISLI_files/`.

## Repository structure

```
MEIH/
├── data/                       # input + supplementary data (Data_S1 … Data_S5)
│   ├── Data_S1_*.xlsx              #   candidate glacial deposits database
│   ├── Data_S2_*.xlsx              #   latitudinal extent of ice (1 Myr resolution)
│   ├── Data_S3_FOAM_files/         #   FOAM climate simulations (.nc)    [git-ignored, large]
│   ├── Data_S4_LMDZ_files/         #   LMDZ climate simulations (.nc)    [git-ignored, large]
│   ├── Data_S5_GRISLI_files/       #   GRISLI ice-sheet model (.nc)      [git-ignored, large]
│   └── processed/                  #   generated outputs                 [git-ignored]
├── src/                        
│   ├── r/                      # R analysis scripts
│   │   └── utils/                  # shared R helpers (particularly lookup tables)
│   └── python/                 # Python analysis scripts
│       └── utils/                  # shared Python helpers
├── figures/                    # figure outputs
├── environment.yml             # conda environment definition
├── MEIH.Rproj                  # RStudio project
└── README.md
```

## Script explanations

| Figure | Language | Script |
| ------ | ---------| ------ |
|   1    | R        | `src/r/meih_fig_1_deposits.R` |
|   2    | Python   | `src/python/meih_fig_2_maps_histograms.py` |
|   3    | Python   | `src/python/meih_fig_3_histograms.py` |
|   4    | Python   | `src/python/meih_fig_4_grisli_south_pole.py` |
|   5    | R        | `src/r/meih_fig_5_glacial_latitudes_through_time.R` |
|  S1    | Python   | `src/python/meih_fig_s1_s2_pgeog.py` |
|  S2    | Python   | `src/python/meih_fig_s1_s2_pgeog.py` |
|  S3    | R        | `src/r/meih_fig_S3-S4_FOAM_seaice.R` |
|  S4    | R        | `src/r/meih_fig_S3-S4_FOAM_seaice.R` |
|  S5    | Python   | `src/python/meih_fig_s5_grisli_initial_kyrs.py` |

## Python environment

The Python code uses a geospatial stack (gplately, pygplates, cartopy, geopandas). 
On Windows these are most reliably installed via conda-forge:

```bash
conda env create -f environment.yml   # or: mamba env create -f environment.yml
conda activate meih
```

## R environment

To work with the R scripts, open `MEIH.Rproj` in RStudio. 
The required R packages are listed in `src/r/dependencies.R`, which installs any necessary packages that are missing from CRAN and loads them. 
Source it once at the start of a session:

```r
source(file.path("src", "r", "dependencies.R"))
```
