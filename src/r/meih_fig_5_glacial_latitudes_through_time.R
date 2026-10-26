# Figure 5: maximum latitudinal extent of low altitude ice through time (Cryogenian to present-day) 
# T. Wong Hearing
# 26 October 2026


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
df <- openxlsx2::wb_to_df(
  file = data_glacials_wb,
  sheet = "latitudinal_extent_of_ice",
  na.strings = "NA"
)
data_glacials <- df[!is.na(names(df))]


# figure 5: latitude of ice from Cryogenian to present ----
## sort data ----
data_to_plot <- data_glacials |>
  dplyr::mutate(
    plot_alpha = dplyr::case_when(
      Glaciation_label == "Early Ediacaran – Tereeken" ~ "possible glaciation", 
      Chronology_notes == "uncertain onset" ~ "uncertain extent",
      Minimum_glaciated_latitude_notes == "uncertain" ~ "uncertain extent",
      .default = "known glaciation"
    ),
    plot_colour = dplyr::case_when(
      Glaciation_label == "Early Ediacaran – Tereeken" ~ "possible glaciation", 
      Chronology_notes == "uncertain onset" ~ "uncertain extent",
      Minimum_glaciated_latitude_notes == "uncertain" ~ "uncertain extent",
      .default = "known glaciation"
    )
  )

## make plot ----
fig5_ice_through_time <- data_to_plot |> 
  ggplot() +
  geom_ribbon(
    aes(x = Age_Ma,
        ymax = 90, 
        ymin = Minimum_glaciated_latitude,
        fill = plot_colour,
        # colour = plot_colour,
        alpha = plot_alpha
    )
  ) +
  labs(
    x = "Age (Ma)",
    y = "Maximum latitudinal extent\nof land ice (° from equator)"
  ) +
  scale_x_reverse(breaks = c(seq(from = 0, to = 700, by = 50))) +
  scale_y_continuous(limits = c(0, 90), breaks = seq(from = 0, to = 90, by = 30)) +
  scale_fill_manual(
    name = "Evidence of ice",
    values = c("known glaciation" = "steelblue", 
               "uncertain extent" = "steelblue", 
               "possible glaciation" = "grey75"
    ), 
    aesthetics = c("fill", "colour")
  ) +
  scale_alpha_manual(
    name = "Evidence of ice",
    values = c("known glaciation" = 1,
               "uncertain extent" = 0.5,
               "possible glaciation" = 0.5),
  ) +
  coord_geo() +
  theme_bw() +
  theme(
    axis.title = element_text(size = 14), 
    axis.text = element_text(size = 12),
    legend.position = "inside",
    legend.justification.inside = c(1, 0),
    legend.position.inside = c(1, 0),
    legend.background = element_rect(fill = "white", colour = "black"), 
    legend.title = element_text(size = 14),
    legend.text = element_text(size = 12)
  ) +
  # annotation to fill the plotting gap between uncertain and certain Marinoan
  annotate(geom = "rect", 
           xmin = 639, xmax = 641, 
           ymin = 0, ymax = 90,
           colour = NA, 
           fill = "steelblue", alpha = 0.5) + 
  # MEIH label
  annotate(
    geom = "text", x = 586, y = 35, label = "MEIH",
    hjust = 1,
    angle = 90, fontface = "bold", colour = "black", size = 12/.pt
  ) +
  # LEIH label
  annotate(
    geom = "text", x = 557, y = 43, label = "LEIH",
    hjust = 1,
    angle = 90, fontface = "bold", colour = "steelblue", alpha = 0.5, 
    size = 12/.pt
  ) 

# show plot
if (isTRUE(plot_show)) {
  print(fig5_ice_through_time)
}

# save plot
if (isTRUE(plot_save)) {
  png(
    filename = file.path(dir_plots, "fig_5_ice_through_time_revised.png"),
    width = 340, height = 120, units = "mm", bg = "white", res = 600
  )
  print(fig5_ice_through_time)
  dev.off() 
}


# END ----