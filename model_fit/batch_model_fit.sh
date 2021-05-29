#!/bin/bash

ld_panel=${1-"ukbb_windowed"}

echo "Submitting jobs for performing model fit using LD panel $ld_panel..."

if [ "$ld_panel" == "ukbb_sample" ]; then
    models=("VIPRS" "vem_c" "VIPRSSBayes")
else
    models=("VIPRS" "vem_c" "VIPRSSBayes" "GibbsPRS" "GibbsPRSSBayes")
fi

for m in "${models[@]}"
do
  rm -rf "./log/model_fit/$ld_panel/$m/*.out" || true
  mkdir -p "./log/model_fit/$ld_panel/$m"
  for ss_file in data/gwas/*/*/*.linear
  do
    sbatch -J "$ld_panel/$m" model_fit/model_fit_job.sh "$ss_file" "$m" "$ld_panel"
  done
done
