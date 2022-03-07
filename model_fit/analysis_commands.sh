#!/bin/bash

# This is a script that lists of the commands that were used for the analyses
# in the VIPRS paper, specifically with respect to model fitting with the different
# variations of the VIPRS model.
#
# !!! IMPORTANT NOTE !!!
# It is not recommended to run this script all at once, as it will launch thousands of jobs
# to the cluster, potentially hitting the limits of the scheduler. We recommend running the commands
# one at a time.

# (1) Analysis to understand impact of LD matrix properties:
python model_fit/batch_model_fit.py -m VIPRS -l ukbb_1k_windowed
python model_fit/batch_model_fit.py -m VIPRS -l ukbb_10k_windowed
python model_fit/batch_model_fit.py -m VIPRS -l ukbb_50k_windowed

python model_fit/batch_model_fit.py -m VIPRS -l ukbb_1k_block
python model_fit/batch_model_fit.py -m VIPRS -l ukbb_10k_block
python model_fit/batch_model_fit.py -m VIPRS -l ukbb_50k_block

python model_fit/batch_model_fit.py -m VIPRS -l ukbb_1k_shrinkage
python model_fit/batch_model_fit.py -m VIPRS -l ukbb_10k_shrinkage
python model_fit/batch_model_fit.py -m VIPRS -l ukbb_50k_shrinkage

# (2) Analysis to understand the impact of priors

python model_fit/batch_model_fit.py -m VIPRSAlpha -l ukbb_50k_windowed
python model_fit/batch_model_fit.py -m VIPRSMix -l ukbb_50k_windowed

# (3) Analysis to understand impact of hyperparameter optimization technique + priors:

# Grid search with performance on held-out validation set as criterion:
python model_fit/batch_model_fit.py -m VIPRS -l ukbb_50k_windowed --strategy GS --opt-params pi --grid-metric validation
python model_fit/batch_model_fit.py -m VIPRSAlpha -l ukbb_50k_windowed --strategy GS --opt-params pi --grid-metric validation
python model_fit/batch_model_fit.py -m VIPRSMix -l ukbb_50k_windowed --strategy GS --opt-params pi --grid-metric validation

# Grid search with ELBO as criterion:
python model_fit/batch_model_fit.py -m VIPRS -l ukbb_50k_windowed --strategy GS --opt-params pi --grid-metric ELBO

# Bayesian Optimization:
python model_fit/batch_model_fit.py -m VIPRS -l ukbb_50k_windowed --strategy BO --opt-params pi --grid-metric ELBO
python model_fit/batch_model_fit.py -m VIPRS -l ukbb_50k_windowed --strategy BO --opt-params pi --grid-metric validation

# Bayesian model averaging:
python model_fit/batch_model_fit.py -m VIPRS -l ukbb_50k_windowed --strategy BMA --opt-params pi
