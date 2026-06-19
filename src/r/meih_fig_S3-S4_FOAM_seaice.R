# Figure S3-S4: FOAM simulated sea ice extent 
# T. Wong Hearing
# 19 June 2026


# clear the decks ----
rm(list = ls())


# set parameters ----
## for plots ----
plot_show <- TRUE
plot_save <- TRUE

## set directory paths ----
## set directory paths ----
dir_data_in <- file.path("data")
dir_foam_sims <- file.path(dir_data_in, "Data_S3_FOAM_files")
dir_plots <- file.path("figures")

# load packages and functions ----
library(ggplot2)
library(dplyr)
library(tidyr)
library(forcats)
library(reshape2)
library(ncdf4)
library(tools)

# load data ----
## get land mask ----
infile_mask <- nc_open(filename = file.path(dir_foam_sims, "600sc_ccm2lnd.nc"), 
                       write = FALSE, suppress_dimvals = FALSE)
mask_lon <- ncvar_get(infile_mask, "lon")
mask_lat <- ncvar_get(infile_mask, "lat")
mask <- ncvar_get(infile_mask, "MASK")

nc_close(infile_mask)

dim_mask_lon <- length(mask_lon)
dim_mask_lat <- length(mask_lat)

land_mask <- matrix(data = 'NA', nrow = dim_mask_lon, ncol = dim_mask_lat)

# make the land mask matrix
for (j in 1:dim_mask_lon){
  for (k in 1:dim_mask_lat){
    land <- as.numeric(mask[j, k]) # extract land mask values
    # convert to a sea mask (i.e. if land -> NA, if sea -> 1)
    if(land == 0){
      land_sea <- 1
    }else{
      land_sea <- NA
    }
    land_mask[j,k] <- land_sea
  }
}
rownames(land_mask) <- mask_lon
colnames(land_mask) <- mask_lat
class(land_mask) <- 'numeric'
# land_mask_long <- melt(land_mask, varnames = c('lon', 'lat'), value.name = 'mask')
# View(land_mask_long)

## get the FOAM simulations ----
orbs <- c("has", "mob")
orbs_long <- c("warm austral summer", "median orbit")
for (i in 1:length(orbs)){
  orb <- orbs[i]
  orb_long <- orbs_long[i]
  # just list files for now, each can be opened and used only when needed later
  infiles_foam_coupl <- list.files(path = dir_foam_sims,
                                   pattern = paste0("^600sc_", orb, "_.*\\_coupl.nc$"),
                                   full.names = FALSE)
  
  ### extract and plot coupler file data ----
  for (j in 1:length(infiles_foam_coupl)) {
    # open file
    infile_name <- file_path_sans_ext(infiles_foam_coupl[j])
    print(infile_name)
    infile <- nc_open(
      filename = file.path(dir_foam_sims, infiles_foam_coupl[j]),
      write = FALSE,
      suppress_dimvals = FALSE
    )
    
    # get dimensions
    lonraw <- ncvar_get(infile, "lon")
    latraw <- ncvar_get(infile, "lat")
    # convert from coupler to ocean grid
    lon <- lonraw - (lonraw[2] - lonraw[1])
    lat <- latraw - (latraw[2] - latraw[1])
    nlon <- dim(lon)
    nlat <- dim(lat)
    t <- ncvar_get(infile, "time")
    nt <- dim(t)
    
    # get ice FRAC variable
    ice_frac <- ncvar_get(infile, 'FRAC')
    
    # close file 
    nc_close(infile)
    
    this_ice_frac_mean_annual = apply(ice_frac, c(1,2), mean, na.rm = TRUE) # average over the third (time) dimension
    this_ice_frac_mean_annual <- as.matrix(this_ice_frac_mean_annual)
    row.names(this_ice_frac_mean_annual) <- lon
    colnames(this_ice_frac_mean_annual) <- lat
    
    this_ice_frac_mean_annual_masked <- this_ice_frac_mean_annual * land_mask
    
    pco2_pal <- paste0(as.numeric(substr(infile_name, 11, 14))/280, " PAL")
    # make long-form
    this_ice_frac_mean_annual_df <- this_ice_frac_mean_annual_masked %>%
      reshape2::melt() %>%
      dplyr::rename(
        lon = Var1,
        lat = Var2,
        !!pco2_pal := value
      )
    
    if (j == 1) {
      ice_frac_mean_annual_df <- this_ice_frac_mean_annual_df
    }else{
      ice_frac_mean_annual_df <- dplyr::left_join(
        ice_frac_mean_annual_df, 
        this_ice_frac_mean_annual_df,
        by = join_by(lon, lat)
      )
    }
  }
  
  ### sort ice fraction data ----
  ice_frac_mean_annual_df_long <- ice_frac_mean_annual_df %>%
    tidyr::pivot_longer(
      cols = ends_with("PAL"),
      names_to = "pCO2",
      values_to = "ice_fraction"
    ) %>%
    dplyr::mutate(
      pCO2 = ordered(
        pCO2,
        levels = c("1 PAL", "2 PAL", "3 PAL", "4 PAL", 
                   "5 PAL", "6 PAL", "7 PAL", "8 PAL", 
                   "9 PAL", "10 PAL", "11 PAL", "12 PAL", 
                   "16 PAL", "32 PAL"
                  )
      )
    ) %>%
    dplyr::group_by(lat, pCO2) %>%
    dplyr::summarise(
      mean = mean(ice_fraction, na.rm = TRUE),
      min = min(ice_fraction, na.rm = TRUE),
      max = max(ice_fraction, na.rm = TRUE)
    ) %>%
    dplyr::mutate(
      mean = ifelse(is.nan(mean), NA, mean),
      min = ifelse(is.infinite(min), NA, min),
      max = ifelse(is.infinite(max), NA, max)
    )
  
  ### make plot ----
  figsX_sea_ice_mean <- ggplot(data = ice_frac_mean_annual_df_long,
                               aes(x = lat, y = mean, ymin = 0, ymax = max)) +
    theme_minimal() +
    theme(panel.grid.minor = element_blank()) +
    labs(
      x = "Latitude (°N)", 
      y = "Zonal annual average grid cell sea ice fraction",
      caption = paste0(orb_long, " orbital configuration")
    ) +
    scale_x_continuous(limits = c(-90, 90), breaks = seq(from = -90, to = 90, by = 45)) + 
    facet_wrap(~pCO2, ncol = 4) +
    geom_ribbon(colour = "skyblue", fill = "skyblue") +
    geom_line(colour = "deepskyblue3", linewidth = 1)
  
  # show plot
  if (isTRUE(plot_show)) { print(figsX_sea_ice_mean) }
  
  # save plot
  if (isTRUE(plot_save)) {
    png(filename = file.path(dir_plots,
                             paste0("fig_s", i+2, "_foam_sea_ice_annual_", orb, ".png")
                             ),
        width = 170, height = 170, units = "mm", bg = "white", res = 600
    )
    print(figsX_sea_ice_mean)
    dev.off()
  }
}


# END ----