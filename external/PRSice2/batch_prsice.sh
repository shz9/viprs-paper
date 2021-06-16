#!/bin/bash

echo "Fitting PRSice2 to summary statistics..."

rm -rf "./log/model_fit/external/PRSice2/" || true
mkdir -p "./log/model_fit/external/PRSice2"

for ss_file in data/gwas/*/*/*.linear
do
  sbatch -J "external/PRSice2" external/PRSice2/fit_prsice.sh "$ss_file"
done
