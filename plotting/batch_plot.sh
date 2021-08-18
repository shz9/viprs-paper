#!/bin/bash
source "$HOME/pyenv/bin/activate"

python plotting/plot_hyperparameter_estimates.py -l ukbb_50k_windowed
python plotting/plot_hyperparameter_estimates.py -l ukbb_50k_block
python plotting/plot_hyperparameter_estimates.py -l ukbb_50k_sample
python plotting/plot_hyperparameter_estimates.py -l ukbb_50k_shrinkage
python plotting/plot_predictive_performance.py
python plotting/plot_time_stats.py 
