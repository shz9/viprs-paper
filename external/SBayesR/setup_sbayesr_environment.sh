#!/bin/bash
# This is a setup script to prepare the bash environment
# for running SBayesR.

# Download SBayesR software (gctb v2.03):

echo "Setting up the environment for SBayesR..."

wget https://cnsgenomics.com/software/gctb/download/gctb_2.03beta_Linux.zip -P external/SBayesR/ || exit

# Unzip and remove the zip file:
unzip external/SBayesR/gctb_2.03beta_Linux.zip -d external/SBayesR/
mv external/SBayesR/gctb_2.03beta_Linux external/SBayesR/gctb_v2.03
rm external/SBayesR/gctb_2.03beta_Linux.zip

# Transform the summary statistics:
# source external/SBayesR/transform_sumstats_job.sh

echo "Done!"
