#!/bin/bash
source "$HOME/pyenv/bin/activate"

python plotting/plot_hyperparameter_estimates.py -l "ukbb_50k_windowed"
python plotting/plot_hyperparameter_estimates.py -l "ukbb_50k_windowed" -t "binary"
#python plotting/plot_hyperparameter_estimates.py -l ukbb_50k_block
#python plotting/plot_hyperparameter_estimates.py -l ukbb_50k_sample
#python plotting/plot_hyperparameter_estimates.py -l ukbb_50k_shrinkage

# Main figures in the manuscript:
python plotting/plot_predictive_performance.py -m "PRSice2,Lassosum,LDPred2-grid,VIPRS,VIPRS-GSvl,SBayesR,PRScs" --prefix "main_figures"
python plotting/plot_predictive_performance.py -t "binary" -m "PRSice2,Lassosum,LDPred2-grid,VIPRS,VIPRS-GSvl,SBayesR,PRScs" --prefix "main_figures"
# Expanded figure (includes more model variations)
python plotting/plot_predictive_performance.py -m "PRSice2,Lassosum,LDPred2-inf,LDPred2-auto,LDPred2-grid,VIPRS,VIPRS-GSvl,VIPRS-BOv,SBayesR,PRScs" --prefix "expanded_figures"
python plotting/plot_predictive_performance.py -t "binary" -m "PRSice2,Lassosum,LDPred2-inf,LDPred2-auto,LDPred2-grid,VIPRS,VIPRS-GSvl,VIPRS-BOv,SBayesR,PRScs" --prefix "expanded_figures"
# Figure that focuses on the hyperparameter search strategies:
python plotting/plot_predictive_performance.py -m "VIPRS,VIPRS-BOv,VIPRS-GSvl,VIPRS-BMA" --prefix "hyperparameter_search"
python plotting/plot_predictive_performance.py -t "binary" -m "VIPRS,VIPRS-BOv,VIPRS-GSvl,VIPRS-BMA" --prefix "hyperparameter_search"
# Figure that focuses on the grid metric:
python plotting/plot_predictive_performance.py -m "VIPRS,VIPRS-BO,VIPRS-BOv,VIPRS-GSvl,VIPRS-GSl" --prefix "grid_metric"
python plotting/plot_predictive_performance.py -t "binary" -m "VIPRS,VIPRS-BO,VIPRS-BOv,VIPRS-GSvl,VIPRS-GSl" --prefix "grid_metric"
# Figure that focuses on Alpha model:
python plotting/plot_predictive_performance.py -m "VIPRS,VIPRSAlpha,VIPRS-GSvl,VIPRSAlpha-GSvl,VIPRS-GSl,VIPRSAlpha-GSl" --prefix "alpha"
python plotting/plot_predictive_performance.py -t "binary" -m "VIPRS,VIPRSAlpha,VIPRS-GSvl,VIPRSAlpha-GSvl,VIPRS-GSl,VIPRSAlpha-GSl" --prefix "alpha"


# Experimental: Examining effect of different VIPRS formulations:
python plotting/plot_predictive_performance.py -m "SBayesR,VIPRS,VIPRS-GSvl,VIPRS_GSv_p,VIPRS-GSvl_e,VIPRS-GSv_e" --prefix "viprs_gs_v"
python plotting/plot_predictive_performance.py -m "SBayesR,VIPRS,VIPRS-GSl,VIPRS_GS_p,VIPRS-GSl_e,VIPRS-GS_e" --prefix "viprs_gs"

python plotting/plot_predictive_performance.py -m "SBayesR,VIPRS,VIPRSAlpha,VIPRSAlpha-GSvl_pe,VIPRSAlpha-GSv_p,VIPRSAlpha-GSvl_e,VIPRSAlpha-GSv_e" --prefix "viprsalpha_gs_v"
python plotting/plot_predictive_performance.py -m "SBayesR,VIPRS,VIPRSAlpha,VIPRSAlpha-GSl_pe,VIPRSAlpha-GS_p,VIPRSAlpha-GSl_e,VIPRSAlpha-GS_e" --prefix "viprsalpha_gs"

python plotting/plot_predictive_performance.py -m "SBayesR,VIPRS,VIPRSSBayes,VIPRSSBayesAlpha,VIPRSSBayes-GS_p,VIPRSSBayesAlpha-GS_p,VIPRSSBayes-GS_p,VIPRSSBayesAlpha-GSv_p" --prefix "viprssbayesalpha_gs"
python plotting/plot_predictive_performance.py -m "SBayesR,VIPRS,VIPRSSBayes,VIPRSSBayes-GS_p,VIPRSSBayes-GSv_p,VIPRSSBayes-GSl_pb,VIPRSSBayes-GSvl_pb" --prefix "viprssbayes_gs"



# Main time figures in the manuscript:
python plotting/plot_time_stats.py -m "PRSice2,Lassosum,LDPred2-grid,VIPRS,VIPRS-GSvl,SBayesR,PRScs" --prefix "main_figures"
# Expanded figure (includes more model variations)
python plotting/plot_time_stats.py -m "PRSice2,Lassosum,LDPred2-inf,LDPred2-auto,LDPred2-grid,VIPRS,VIPRS-GSvl,VIPRS-BOv,SBayesR,PRScs" --prefix "expanded_figures"

