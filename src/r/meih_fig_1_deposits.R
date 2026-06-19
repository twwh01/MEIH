# Figure 1: glaciogenic sedimentary deposits and scores through time 
# T. Wong Hearing
# 19 June 2026
#
# Updated from Wong Hearing et al (2026)


# clear the decks ----
rm(list = ls())


# set parameters ----
## for plots ----
plot_age_lims <- c(650, 510) # in Ma for reverse age axis
shade_value <- 0.3
plot_show <- TRUE
plot_save <- TRUE

## set directory paths ----
dir_data_in <- file.path("data")
dir_plots <- file.path("figures")

## load glaciation intervals ----
source(file = file.path("src", "r", "utils", "ecesd_glaciations_table.R"))

## load deeptime palette ----
source(file = file.path("src", "r", "utils", "ecesd_deeptime_dat.R"))


# load packages and functions ----
library(openxlsx2) # for opening data file
library(ggplot2) # for plotting
library(deeptime) # for plotting with GTS
library(ggpubr) # for when patchwork doesn't work so well
library(dplyr)
library(forcats)


# load glacial deposits data ----
## load workbook ----
# infile_name <- "Data_S1_MEIH_deposits_raw.xlsx"
infile_name <- "Data_S1_MEIH_deposits_raw.xlsx"
infile <- openxlsx2::wb_load(file = file.path(dir_data_in, infile_name))

## load data sheets ----
# load unique deposits
data_csl_deposits <- openxlsx2::wb_to_df(file = infile, 
                                         sheet = "csl_deposits",
                                         na.strings = "NA") 

# load deposit dates
data_csl_dates <- openxlsx2::wb_to_df(file = infile,
                                      sheet = "csl_age_constraints",
                                      na.strings = "NA")

# sort data ----
## sort deposit data ----
# reduce deposit information to only what is necessary
data_csl_deposits_abbr <- data_csl_deposits %>%
  dplyr::select(deposit_id, 
                deposit_name,
                likely_interval,
                likely_interval_notes,
                deposit_score_WH02,
                deposit_score_WH02_source,
                deposit_score_WH01,
                deposit_score_WH01_source, 
                deposit_score_Tindal2023, 
                deposit_score_Tindal2023_notes) %>%
  # convert scores to factors
  dplyr::mutate(deposit_score_WH02 = ordered(deposit_score_WH02,
                                             levels = c(NA, 0, 1, 2, 3, 4, 5)), 
                deposit_score_WH01 = ordered(deposit_score_WH01,
                                             levels = c(NA, 0, 1, 2, 3, 4, 5)))


## combine date and deposit information ----
data_deposits_fig1 <- data_csl_dates %>%
  dplyr::left_join(., data_csl_deposits_abbr, 
                   by = join_by(deposit_id, deposit_name)) %>%
  dplyr::select(deposit_name, 
                deposit_score_WH02, 
                likely_interval, 
                constraint_wrt_csl,
                constraint_position, 
                constraint_type, 
                constraint_date_type, 
                constraint_date_system, 
                constraint_age_ma,
                constraint_age_ma_unc) %>% 
  dplyr::mutate(deposit_score_WH02 = as.numeric(as.character(deposit_score_WH02)), 
                alf = ifelse(deposit_score_WH02 > 2, 1, shade_value)) %>%
  dplyr::filter(
    # remove entries with no age constraint (shouldn't be any in the dataset but just to be sure)
    !is.na(constraint_age_ma),
    # remove dates beyond plot age limits
    (constraint_age_ma < max(plot_age_lims, na.rm = TRUE) & 
       constraint_age_ma > min(plot_age_lims, na.rm = TRUE)),
    # remove the Doushantuo Formation entries
    !(deposit_name %in% c("Doushantuo Formation", "Doushantuo glendonites")),
    # remove any entries that are likely Cryogenian
    likely_interval != "Cryogenian",
    # remove any entries with Rb-Sr whole-rock dates as these are not considered reliable here
    (is.na(constraint_date_system) | constraint_date_system != "Rb-Sr"),
    !is.na(constraint_wrt_csl), 
    # remove NA score deposits
    # these should not be plotted but may have location or date entries from previous
    # iterations of the dataset (e.g. if they were given a score value by Tindal 2023 or WH01)
    !is.na(deposit_score_WH02)
  ) %>%
  dplyr::mutate(
    # merge "Cambrian" with "uncertain" deposits
    likely_interval = ordered(case_when(likely_interval == "Cambrian" ~ "uncertain", 
                                        .default = likely_interval),
                              levels = c("uncertain", "Ediacaran", "MEIH", "LEGH", "LEIH", "TEGH")),
    # add a new variable for colour in the plots reflecting the dating method
    plot_colour_date_type = ordered(case_when(constraint_type == "Radiometric date" ~ paste0("Radiometric: ", constraint_date_system),
                                              # constraint_type == "CIE" ~ "Shuram CIE", 
                                              .default = constraint_type), 
                                    levels = c("Radiometric: U-Pb",
                                               "Radiometric: Re-Os", 
                                               "Radiometric: Pb-Pb",
                                               "Radiometric: Ar-Ar",
                                               "Biostratigraphy",
                                               "Correlation",
                                               # "Shuram CIE"
                                               "CIE")),
    plot_shape_constraint = ordered(constraint_wrt_csl, 
                                    levels = c("maximum", "deposition", "minimum")))

## recalculate min/max age constraints ----
data_ages_minmax_fig1 <- data_deposits_fig1 %>%
  # calculate each age with analytical uncertainty where relevant
  dplyr::mutate(age_ma_min_unc = ifelse(!is.na(constraint_age_ma - constraint_age_ma_unc),
                                        constraint_age_ma - constraint_age_ma_unc,
                                        constraint_age_ma),
                age_ma_max_unc = ifelse(!is.na(constraint_age_ma + constraint_age_ma_unc),
                                        constraint_age_ma + constraint_age_ma_unc,
                                        constraint_age_ma)) %>%
  dplyr::ungroup() %>%
  dplyr::group_by(deposit_name, 
                  deposit_score_WH02, 
                  likely_interval, 
                  alf) %>%
  dplyr::summarise(
    plot_date_max = dplyr::case_when(
      !is.infinite(min(constraint_age_ma[plot_shape_constraint == "deposition" | plot_shape_constraint == "maximum"], na.rm = TRUE)) ~ min(constraint_age_ma[plot_shape_constraint == "deposition" | plot_shape_constraint == "maximum"], na.rm = TRUE),
      .default = 1000
    ),
    plot_date_max_unc = dplyr::case_when(
      !is.infinite(min(age_ma_max_unc[plot_shape_constraint == "deposition" | plot_shape_constraint == "maximum"], na.rm = TRUE)) ~ min(age_ma_max_unc[plot_shape_constraint == "deposition" | plot_shape_constraint == "maximum"], na.rm = TRUE),
      .default = 1000
    ),
    plot_date_min = dplyr::case_when(
      !is.infinite(max(constraint_age_ma[plot_shape_constraint == "minimum"], na.rm = TRUE)) ~ max(constraint_age_ma[plot_shape_constraint == "minimum"], na.rm = TRUE),
      .default = 0
    ),
    plot_date_min_unc = dplyr::case_when(
      !is.infinite(max(age_ma_min_unc[plot_shape_constraint == "minimum"], na.rm = TRUE)) ~ max(age_ma_min_unc[plot_shape_constraint == "minimum"], na.rm = TRUE),
      .default = 0
    ),
    .groups = "keep"
  )

## order deposits by maximum age constraint ----
data_deposits_fig1 <- data_deposits_fig1 %>%
  dplyr::mutate(deposit_name = ordered(deposit_name,
                                       levels = unique(data_ages_minmax_fig1$deposit_name[order(-data_ages_minmax_fig1$alf, 
                                                                                                -data_ages_minmax_fig1$deposit_score_WH02, 
                                                                                                data_ages_minmax_fig1$plot_date_max,
                                                                                                decreasing = TRUE)]))) 

## extract score information ----
data_scores_fig1 <- data_deposits_fig1 %>%
  dplyr::distinct(deposit_name, deposit_score_WH02, alf, likely_interval)


# plot figure 1: MEIH temporal distribution ----
## plot figure 1 scores ----
plot_fig1_deposit_scores <- ggplot(data = data_scores_fig1,
                                   aes(x = deposit_score_WH02,
                                       y = deposit_name)) +
  geom_col(aes(alpha = alf),
           fill = "steelblue") +
  geom_vline(xintercept = 2,
             linetype = "dashed",
             colour = "grey50") +
  scale_alpha_identity(guide = "none") +
  scale_y_discrete(name = "Candidate glacial deposits",
                   expand = expansion(add = 0.45)) +
  scale_x_reverse(name = "Deposit\nscore", 
                  limits = c(5, 0),
                  breaks = seq(from = 5, to = 0, by = -1),
                  expand = expansion(add = c(0.1, 0.1))) +
  facet_grid(fct_rev(likely_interval) ~ ., 
             scales = "free_y",
             space = "free_y",
             drop = TRUE) +
  theme_bw() +
  theme(strip.background = element_blank(),
        strip.text = element_blank(),
        axis.title = element_text(size = 8),
        axis.text.x = element_text(size = 6),
        axis.text.y = element_text(angle = 0, vjust = 0.3, hjust = 1, size = 6),
        panel.grid.major.x = element_blank(),
        panel.grid.minor.x = element_blank(),
        plot.margin = unit(c(0, 0, 0, 0.5), "cm"))
# have a check
if(isTRUE(plot_show)){
  print(plot_fig1_deposit_scores)
}

## plot figure 1 dates ----
plot_fig1_deposit_dates <- ggplot() +
  # annotate with icehouse intervals
  geom_rect(data = ecesd_glaciations,
            aes(xmin = Age_min, 
                xmax = Age_max, 
                ymin = -Inf, 
                ymax = Inf),
            alpha = 0.3,
            fill = "steelblue",
            colour = "steelblue") +
  # annotate with E-C boundary
  geom_vline(xintercept = c(538.8, 635), linetype = "dashed", colour = "grey50") +
  # add solid line between min and max age ranges
  geom_linerange(data = data_ages_minmax_fig1,
                 aes(y = deposit_name, 
                     xmin = plot_date_min_unc, 
                     xmax = plot_date_max_unc, 
                     alpha = alf),
                 position = "identity",
                 linetype = "solid",
                 linewidth = 1,
                 colour = "black") +
  geom_linerange(data = data_deposits_fig1,
                 aes(x = constraint_age_ma,
                     y = deposit_name,
                     xmin = constraint_age_ma - constraint_age_ma_unc,
                     xmax = constraint_age_ma + constraint_age_ma_unc,
                     colour = plot_colour_date_type,
                     alpha = alf,
                     group = deposit_name),
                 linewidth = 0.5) +
  # add individual dates as points
  geom_point(data = data_deposits_fig1,
             aes(x = constraint_age_ma, 
                 y = deposit_name,
                 shape = plot_shape_constraint,
                 colour = plot_colour_date_type,
                 alpha = alf,
                 group = deposit_name), 
             size = 3,
             stroke = 1) +
  # add an empty geom_col to align with score columns when panel plotting
  geom_col(data = data_deposits_fig1, aes(x = 0, y = deposit_name)) +
  scale_shape_manual(values = c("maximum" = -9658, #24,
                                "deposition" = 18,
                                "minimum" = -9668 #25
                                ),
                     na.value = NA,
                     breaks = c( "maximum", "deposition", "minimum", NA)) +
  scale_colour_viridis_d(option = "turbo", 
                         begin = 0.1, 
                         end = 0.9,
                         direction = -1, 
                         na.value = "grey25") +
  scale_alpha_identity(guide = "none") +
  # add scale_x expansion to allow alignment with geom_col below
  scale_y_discrete(expand = expansion(add = 2)) +
  scale_x_reverse(breaks = seq(from = min(plot_age_lims-10), to = max(plot_age_lims), by = 20),
                  expand = expansion(add = 2)) +
  labs(x = "Age (Ma)",
       y = "Candidate glacial deposits",
       shape = "Constraint",
       colour = "Date type") +
  coord_geo(pos = "top", 
            height = unit(1, "line"),
            dat = ECESD_dt_MS1F1, 
            xlim = plot_age_lims) +
  facet_grid(fct_rev(likely_interval) ~ ., 
             scales = "free_y",
             space = "free_y",
             drop = TRUE) +
  guides(colour = guide_legend(nrow = 1, order = 1),
         shape = guide_legend(order = 2)) + 
  theme_bw() +
  # theme edited to work with panel plot
  # remove x-axis details and sort plot margins
  theme(axis.title.y = element_blank(),
        axis.text.y = element_blank(),
        axis.ticks.length.y = unit(0, "cm"),
        axis.title.x = element_text(size = 8),
        axis.text.x = element_text(size = 6),
        strip.background = element_blank(), 
        strip.text.y = element_text(size = 6, angle = -90, hjust = 0.5, colour = "black", face = "bold"),
        plot.margin = unit(c(0.5, 0, 0, 0), "cm"), 
        panel.grid.major.x = element_blank(),
        panel.grid.minor.x = element_blank(),
        legend.direction = "horizontal", 
        legend.box = "vertical",
        legend.box.just = "right",
        legend.box.spacing = unit(1, "pt"),
        legend.position = "bottom",
        legend.justification.bottom = "right",
        legend.spacing.x = unit(0, "pt"),
        legend.spacing.y = unit(0, "pt"),
        legend.background = element_rect(fill = "white", colour = NA),
        legend.title = element_text(size = 8),
        legend.text = element_text(size = 6, margin = margin(0, 0, 0, 0)),
        legend.margin = margin(0, 0, 0, 0, unit = "pt"))
# have a check
if(isTRUE(plot_show)){
  print(plot_fig1_deposit_dates)
}

## combine as panel plot ----
plot_fig1_panel <- ggarrange(plot_fig1_deposit_scores, plot_fig1_deposit_dates,
                             ncol = 2, align = "h", widths = c(0.5, 1))
# have a check
if(isTRUE(plot_show)){
  plot_fig1_panel
}

if(isTRUE(plot_save)) {
  png(file = file.path(dir_plots, "fig_1_deposits_dates_scores.png"),
      width = 176, height = 210, units = "mm",
      bg = "white", res = 450)
  print(plot_fig1_panel)
  dev.off()
}


# END ----