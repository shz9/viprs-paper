#!/bin/bash

rm -rf ./log/model_fit/*.out || true
mkdir -p ./log/model_fit/

echo "Submitting jobs for performing model fit..."

models=("vem_c" "gibbs_c" "vem_c_sbayes" "prs_gibbs_sbayes")

for m in "${models[@]}"
do
  for ss_file in data/gwas/*/*/*.linear
  do
    sbatch model_fit/model_fit_job.sh "$ss_file" "$m"
  done
done