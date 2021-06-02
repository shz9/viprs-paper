#!/bin/bash

ld_panel=${1-"ukbb_windowed"}

echo "Submitting jobs for performing model fit using LD panel $ld_panel..."

if [ "$ld_panel" == "ukbb_sample" ]; then
    models=("VIPRS" "VIPRSSBayes")
    fit_method=("EM")
else
    models=("VIPRS" "VIPRSSBayes" "GibbsPRS" "GibbsPRSSBayes")
    fit_method=("EM" "BAM" "BO" "GS")
fi

for fm in "${fit_method[@]}"
do
  for m in "${models[@]}"
  do

    if [[ $m == *"Gibbs"* && $fm == "BAM" ]]; then
      continue
    fi

    if [ "$fm" == "EM" ]; then
      model_name=$m
    else
      model_name="$m-$fm"
    fi

    rm -rf "./log/model_fit/$ld_panel/$model_name/*.out" || true
    mkdir -p "./log/model_fit/$ld_panel/$model_name"

    for ss_file in data/gwas/*/*/*.linear
    do
      sbatch -J "$ld_panel/$model_name" model_fit/model_fit_job.sh "$ss_file" "$m" "$ld_panel" "$fm"
    done

  done
done
