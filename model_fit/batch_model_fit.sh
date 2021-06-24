#!/bin/bash

ld_panel=${1-"ukbb_50k_windowed"}
sumstats_dir=${2-"real"}

echo "Submitting jobs for performing model fit using LD panel $ld_panel..."
echo "and summary statistics from directory $sumstats_dir"

if [[ $ld_panel == *"sample"* ]]; then
    models=("VIPRS" "VIPRSSBayes")
    fit_method=("EM")
else
    models=("VIPRS" "VIPRSSBayes" "GibbsPRS" "GibbsPRSSBayes")
    fit_method=("EM" "BMA" "BO" "GS")
fi

for fm in "${fit_method[@]}"
do
  for m in "${models[@]}"
  do

    if [[ $m == *"Gibbs"* && $fm != "EM" ]]; then
      continue
    fi

    if [ "$fm" == "EM" ]; then
      model_name=$m
    else
      model_name="$m-$fm"
    fi

    rm -rf "./log/model_fit/$ld_panel/$model_name/$sumstats_dir" || true
    mkdir -p "./log/model_fit/$ld_panel/$model_name/$sumstats_dir"

    echo "Submitting jobs for model $model_name..."

    for ss_file in data/gwas/"$sumstats_dir"/*/*.linear
    do
      sbatch -J "$ld_panel/$model_name/$sumstats_dir" model_fit/model_fit_job.sh "$ss_file" "$m" "$ld_panel" "$fm"
    done

  done
done
