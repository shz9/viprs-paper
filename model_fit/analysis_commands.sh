#!/bin/bash

# This is a script that lists of the commands that were used for the analyses
# in the VIPRS paper, specifically with respect to model fitting with the different
# variations of the VIPRS model.
#
# !!! IMPORTANT NOTE !!!
# It is not recommended to run this script all at once, as it will launch thousands of jobs
# to the cluster, potentially hitting the limits of the scheduler. It is better to run the commands
# one at a time.

python model_fit/batch_model_fit.py -m VIPRS -l ukbb_1k_windowed
python model_fit/batch_model_fit.py -m VIPRS -l ukbb_10k_windowed
python model_fit/batch_model_fit.py -m VIPRS -l ukbb_50k_windowed





python model_fit/batch_model_fit.py -m VIPRS -l ukbb_1k_block
python model_fit/batch_model_fit.py -m VIPRS -l ukbb_10k_block
python model_fit/batch_model_fit.py -m VIPRS -l ukbb_50k_block

python model_fit/batch_model_fit.py -m VIPRS -l ukbb_1k_shrinkage
python model_fit/batch_model_fit.py -m VIPRS -l ukbb_10k_shrinkage
python model_fit/batch_model_fit.py -m VIPRS -l ukbb_50k_shrinkage

python model_fit/batch_model_fit.py -m VIPRSAlpha -l ukbb_1k_windowed
python model_fit/batch_model_fit.py -m VIPRSAlpha -l ukbb_10k_windowed
python model_fit/batch_model_fit.py -m VIPRSAlpha -l ukbb_50k_windowed

python model_fit/batch_model_fit.py -m VIPRSAlpha -l ukbb_1k_block
python model_fit/batch_model_fit.py -m VIPRSAlpha -l ukbb_10k_block
python model_fit/batch_model_fit.py -m VIPRSAlpha -l ukbb_50k_block

python model_fit/batch_model_fit.py -m VIPRSAlpha -l ukbb_1k_shrinkage
python model_fit/batch_model_fit.py -m VIPRSAlpha -l ukbb_10k_shrinkage
python model_fit/batch_model_fit.py -m VIPRSAlpha -l ukbb_50k_shrinkage

python model_fit/batch_model_fit.py -m VIPRSMix -l ukbb_1k_windowed
python model_fit/batch_model_fit.py -m VIPRSMix -l ukbb_10k_windowed
python model_fit/batch_model_fit.py -m VIPRSMix -l ukbb_50k_windowed

python model_fit/batch_model_fit.py -m VIPRSMix -l ukbb_1k_block
python model_fit/batch_model_fit.py -m VIPRSMix -l ukbb_10k_block



python model_fit/batch_model_fit.py -m VIPRSMix -l ukbb_50k_block

python model_fit/batch_model_fit.py -m VIPRSMix -l ukbb_1k_shrinkage
python model_fit/batch_model_fit.py -m VIPRSMix -l ukbb_10k_shrinkage
python model_fit/batch_model_fit.py -m VIPRSMix -l ukbb_50k_shrinkage




