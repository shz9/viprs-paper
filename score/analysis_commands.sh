#!/bin/bash

# This is a script that lists of the commands that were used for the analyses
# in the VIPRS paper, specifically with respect to model scoring with the different
# variations of the VIPRS model.
#
# !!! IMPORTANT NOTE !!!
# It is not recommended to run this script all at once, as it will launch thousands of jobs
# to the cluster, potentially hitting the limits of the scheduler. We recommend running the commands
# one at a time.

# (1) Analysis to understand impact of LD matrix properties:
python score/batch_score.py -m VIPRS -l ukbb_1k_windowed
python score/batch_score.py -m VIPRS -l ukbb_10k_windowed
python score/batch_score.py -m VIPRS -l ukbb_50k_windowed

python score/batch_score.py -m VIPRS -l ukbb_1k_block
python score/batch_score.py -m VIPRS -l ukbb_10k_block
python score/batch_score.py -m VIPRS -l ukbb_50k_block

python score/batch_score.py -m VIPRS -l ukbb_1k_shrinkage
python score/batch_score.py -m VIPRS -l ukbb_10k_shrinkage
python score/batch_score.py -m VIPRS -l ukbb_50k_shrinkage

# (2) Analysis to understand the impact of priors

python score/batch_score.py -m VIPRSAlpha -l ukbb_50k_windowed
python score/batch_score.py -m VIPRSMix -l ukbb_50k_windowed

# (3) Analysis to understand impact of hyperparameter optimization technique + priors:

# Grid search with performance on held-out validation set as criterion:
python score/batch_score.py -m VIPRS-GSv_p -l ukbb_50k_windowed
python score/batch_score.py -m VIPRSAlpha-GSv_p -l ukbb_50k_windowed
python score/batch_score.py -m VIPRSMix-GSv_p -l ukbb_50k_windowed

# Grid search with ELBO as criterion:
python score/batch_score.py -m VIPRS-GS_p -l ukbb_50k_windowed

# Bayesian Optimization:
python score/batch_score.py -m VIPRS-BO_p -l ukbb_50k_windowed
python score/batch_score.py -m VIPRS-BOv_p -l ukbb_50k_windowed

# Bayesian model averaging:
python score/batch_score.py -m VIPRS-BMA_p -l ukbb_50k_windowed
