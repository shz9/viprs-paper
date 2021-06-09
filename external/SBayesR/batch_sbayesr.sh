#!/bin/bash

echo "Fitting SBayesR to summary statistics..."

ldm="$HOME/projects/def-sgravel/data/ld/ukbEURu_hm3_shrunk_sparse/ukbEURu_hm3_chr22_v3_50k.ldm.sparse"

rm -rf "./log/model_fit/ukbb_50k_ld/sbayesr/*.out" || true
mkdir -p "./log/model_fit/ukbb_50k_ld/sbayesr"

for ss_file in data/gwas/*/*/*.ma
do
  sbatch -J "ukbb_50k_ld/sbayesr" external/SBayesR/fit_sbayesr.sh "$ldm" "$ss_file"
done
