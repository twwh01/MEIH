# Dependencies for the MEIH R project
#
# This script will install from CRAN all the necessary R packages for these analyses. 
# This script only needs to be sourced once at the start of a session. 
# In the R console, you can run:
#   source(file.path("src", "r", "dependencies.R"))
# Depending on your local R configuration, you may need to run this script with appropriate permissions. 
#
# See environment.yml for the parallel Python environment.

r_dependencies <- c(
  # data loading
  "openxlsx2",  # read the supplementary .xlsx data files (fig 1, fig 5)
  "ncdf4",      # read NetCDF model output (figs S3-S4)

  # data wrangling
  "dplyr",      # data manipulation (all figures)
  "tidyr",      # pivot_longer (figs S3-S4)
  "reshape2",   # melt (figs S3-S4)
  "forcats",    # factor reordering, e.g. fct_rev (fig 1, figs S3-S4)

  # plotting
  "ggplot2",    # plotting (all figures)
  "deeptime",   # geological time-scale axes via coord_geo (fig 1, fig 5)
  "ggpubr"      # arrange multi-panel figures via ggarrange (fig 1)
)

# install any that are missing, then load them all
for (pkg in r_dependencies) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    install.packages(pkg)
  }
}

rm(pkg)
