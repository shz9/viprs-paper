#!/bin/bash

ld_panel=${1-"ukbb_windowed"}

rm -rf "./log/model_fit/$ld_panel/*.out" || true
mkdir -p "./log/model_fit/$ld_panel"

echo "Submitting jobs for performing model fit using LD panel $ld_panel..."

models=("VIPRS" "vem_c" "VIPRSSBayes" "GibbsPRS" "GibbsPRSSBayes")
#("vem_c" "gibbs_c" "vem_c_sbayes" "prs_gibbs_sbayes")

for m in "${models[@]}"
do
  for ss_file in data/gwas/*/*/*.linear
  do
    sbatch -J "$ld_panel" model_fit/model_fit_job.sh "$ss_file" "$m" "$ld_panel"
  done
done
