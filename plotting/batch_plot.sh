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

# Main time figures in the manuscript:
python plotting/plot_time_stats.py -m "PRSice2,Lassosum,LDPred2-grid,VIPRS,VIPRS-GSvl,SBayesR,PRScs" --prefix "main_figures"
# Expanded figure (includes more model variations)
python plotting/plot_time_stats.py -m "PRSice2,Lassosum,LDPred2-inf,LDPred2-auto,LDPred2-grid,VIPRS,VIPRS-GSvl,VIPRS-BOv,SBayesR,PRScs" --prefix "expanded_figures"

