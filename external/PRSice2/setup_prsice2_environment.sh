#!/bin/bash
# This is a setup script to prepare the bash/R environment
# for running PRSice2.

# Download PRSice2 software:
wget https://github.com/choishingwan/PRSice/releases/download/2.3.5/PRSice_linux.zip -P external/PRSice2/ || exit

# Unzip the software:
unzip external/PRSice2/PRSice_linux.zip -d external/PRSice2/PRSice_linux
mv external/PRSice2/PRSice_linux external/PRSice2/PRSice_v2.3.5
rm external/PRSice2/PRSice_linux.zip

# Install all the required R packages

module load gcc/9.3.0 r/4.0.2
mkdir -p "external/PRSice2/R_PRSice2_env" || true

export R_LIBS="external/PRSice2/R_PRSice2_env"

Rscript external/PRSice2/PRSice_v2.3.5/PRSice.R

echo "Done!"

