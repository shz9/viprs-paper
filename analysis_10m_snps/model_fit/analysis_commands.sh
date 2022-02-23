#!/bin/bash

# This is a script that lists of the commands that were used for the analyses
# in the VIPRS paper, specifically with respect to model fitting with the different
# variations of the VIPRS model.
#
# !!! IMPORTANT NOTE !!!
# It is not recommended to run this script all at once, as it will launch thousands of jobs
# to the cluster, potentially hitting the limits of the scheduler. It is better to run the commands
# one at a time.

python analysis_10m_snps/model_fit/batch_model_fit.py -m VIPRS -t binary
python analysis_10m_snps/model_fit/batch_model_fit.py -m VIPRS -t quantitative -p HEIGHT
python analysis_10m_snps/model_fit/batch_model_fit.py -m VIPRS -t quantitative -p BMI
python analysis_10m_snps/model_fit/batch_model_fit.py -m VIPRS -t quantitative -p BW
python analysis_10m_snps/model_fit/batch_model_fit.py -m VIPRS -t quantitative -p FEV1
python analysis_10m_snps/model_fit/batch_model_fit.py -m VIPRS -t quantitative -p FVC
python analysis_10m_snps/model_fit/batch_model_fit.py -m VIPRS -t quantitative -p HC
python analysis_10m_snps/model_fit/batch_model_fit.py -m VIPRS -t quantitative -p HDL
python analysis_10m_snps/model_fit/batch_model_fit.py -m VIPRS -t quantitative -p LDL
python analysis_10m_snps/model_fit/batch_model_fit.py -m VIPRS -t quantitative -p WC

python analysis_10m_snps/model_fit/batch_model_fit.py -m VIPRSMix -t binary
python analysis_10m_snps/model_fit/batch_model_fit.py -m VIPRSMix -t quantitative -p HEIGHT
python analysis_10m_snps/model_fit/batch_model_fit.py -m VIPRSMix -t quantitative -p BMI
python analysis_10m_snps/model_fit/batch_model_fit.py -m VIPRSMix -t quantitative -p BW
python analysis_10m_snps/model_fit/batch_model_fit.py -m VIPRSMix -t quantitative -p FEV1
python analysis_10m_snps/model_fit/batch_model_fit.py -m VIPRSMix -t quantitative -p FVC
python analysis_10m_snps/model_fit/batch_model_fit.py -m VIPRSMix -t quantitative -p HC
python analysis_10m_snps/model_fit/batch_model_fit.py -m VIPRSMix -t quantitative -p HDL
python analysis_10m_snps/model_fit/batch_model_fit.py -m VIPRSMix -t quantitative -p LDL
python analysis_10m_snps/model_fit/batch_model_fit.py -m VIPRSMix -t quantitative -p WC

python analysis_10m_snps/model_fit/batch_model_fit.py -m VIPRSAlpha -t binary
python analysis_10m_snps/model_fit/batch_model_fit.py -m VIPRSAlpha -t quantitative -p HEIGHT
python analysis_10m_snps/model_fit/batch_model_fit.py -m VIPRSAlpha -t quantitative -p BMI
python analysis_10m_snps/model_fit/batch_model_fit.py -m VIPRSAlpha -t quantitative -p BW
python analysis_10m_snps/model_fit/batch_model_fit.py -m VIPRSAlpha -t quantitative -p FEV1
python analysis_10m_snps/model_fit/batch_model_fit.py -m VIPRSAlpha -t quantitative -p FVC
python analysis_10m_snps/model_fit/batch_model_fit.py -m VIPRSAlpha -t quantitative -p HC
python analysis_10m_snps/model_fit/batch_model_fit.py -m VIPRSAlpha -t quantitative -p HDL
python analysis_10m_snps/model_fit/batch_model_fit.py -m VIPRSAlpha -t quantitative -p LDL
python analysis_10m_snps/model_fit/batch_model_fit.py -m VIPRSAlpha -t quantitative -p WC


