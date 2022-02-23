#!/bin/bash

# This is a script that lists of the commands that were used for the analyses
# in the VIPRS paper, specifically with respect to model scoring with the different
# variations of the VIPRS model.

python analysis_10m_snps/score/batch_score.py -m VIPRS
python analysis_10m_snps/score/batch_score.py -m VIPRSMix
python analysis_10m_snps/score/batch_score.py -m VIPRSAlpha
