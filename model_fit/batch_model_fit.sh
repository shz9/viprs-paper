#!/bin/bash

rm -rf ./log/model_fit/*.out || true
mkdir -p ./log/model_fit/

echo "Submitting jobs for performing model fit..."

ld_panels=("ukbb_windowed" "ukbb_shrinkage" "ukbb_sample")
models=("VIPRS" "VIPRSSBayes" "GibbsPRS" "GibbsPRSSBayes")
#("vem_c" "gibbs_c" "vem_c_sbayes" "prs_gibbs_sbayes")

for m in "${models[@]}"
do
  for ld in "${ld_panels[@]}"
  do
    for ss_file in data/gwas/*/*/*.linear
    do
      sbatch model_fit/model_fit_job.sh "$ss_file" "$m" "$ld"
    done
  done
done
