# Figure 5: maximum latitudinal extent of low altitude ice through time (Cryogenian to present-day) 
# T. Wong Hearing
# 19 June 2026


# clear the decks ----
rm(list = ls())


# set parameters ----
## for plots ----
plot_show <- TRUE
plot_save <- TRUE

## set directory paths ----
dir_data_in <- file.path("data")
dir_plots <- file.path("figures")


# load packages and functions ----
library(openxlsx2) # for opening data file
library(ggplot2) # for plotting
library(deeptime) # for plotting with GTS
library(dplyr)


# load glacial ice latitudinal extent data ----
data_glacials_wb <- openxlsx2::wb_load(
  file = file.path(dir_data_in, "Data_S2_ice_latitude_extent_1Myr.xlsx")
)
data_glacials <- openxlsx2::wb_to_df(
  file = data_glacials_wb,
  sheet = "latitudinal_extent_of_ice",
  na.strings = "NA"
)


# figure 5: latitude of ice from Cryogenian to present ----
## sort data ----
data_glacials_uncertain <- data_glacials %>%
  dplyr::filter(
    Minimum_glaciated_latitude_notes == "uncertain",
    Age_Ma > 570
  )
data_glacials_leih <- data_glacials %>%
  dplyr::filter(
    Minimum_glaciated_latitude_notes == "uncertain",
    Age_Ma < 570
  )

## make plot ----
fig5_ice_through_time <- ggplot() +
  labs(
    x = "Age (Ma)",
    y = "Maximum latitudinal extent of ice\n(° from equator)",
    colour = "Evidence of\nice extent:"
  ) +
  scale_x_reverse() +
  scale_y_continuous(limits = c(0, 90), breaks = seq(from = 0, to = 90, by = 30)) +
  scale_alpha_manual(
    values = c("NA" = 1, "uncertain onset" = 0.25), 
    guide = "none"
  ) +
  scale_colour_manual(
    values = c("known" = "steelblue", "LEIH" = "steelblue", "uncertain" = "grey80")
  ) +
  coord_geo() +
  theme_bw() +
  theme(
    axis.title = element_text(size = 14), 
    axis.text = element_text(size = 12),
    legend.position = "inside",
    legend.position.inside = c(0.95, 0.2),
    legend.background = element_rect(fill = "white", colour = "black"), 
    legend.title = element_text(size = 14),
    legend.text = element_text(size = 12)
  ) +
  geom_segment(
    data = data_glacials_uncertain,
    aes(x = Age_Ma, y = 0, yend = 90, colour = "uncertain"),
    linewidth = 0.5, linetype = "dashed"
  ) +
  geom_segment(
    data = data_glacials_leih,
    aes(x = Age_Ma, y = 0, yend = 90, colour = "LEIH"),
    linewidth = 0.5, linetype = "dashed"
  ) +
  geom_segment(
    data = data_glacials,
    aes(x = Age_Ma, y = Minimum_glaciated_latitude, yend = 90, 
        alpha = Chronology_notes, colour = "known"),
    linewidth = 1
  ) +
  geom_segment(
    aes(x = 586, y = 20, xend = 586, yend = 35),
    arrow = arrow(length = unit(3, "mm"), angle = 20, type = "open"),
    color = "black",
    linewidth = 1.5,
    linetype = "solid"
  ) +
  annotate(
    geom = "text", x = 586, y = 12, label = "MEIH",
    angle = 90, fontface = "bold", colour = "black", size = 12/.pt
  )

# show plot
if (isTRUE(plot_show)) {
  print(fig5_ice_through_time)
}

# save plot
if (isTRUE(plot_save)) {
  png(
    filename = file.path(dir_plots, "fig_5_ice_through_time.png"),
    width = 340, height = 120, units = "mm", bg = "white", res = 600
  )
  print(fig5_ice_through_time)
  dev.off() 
}


# END ----