#!/bin/bash

ld_panel=${1-"ukbb_50k_windowed"}

echo "Submitting jobs for performing model fit using LD panel $ld_panel..."

if [[ $ld_panel == *"sample"* ]]; then
    models=("VIPRS" "VIPRSSBayes")
    fit_method=("EM")
else
    models=("VIPRS" "VIPRSSBayes" "GibbsPRS" "GibbsPRSSBayes")
    fit_method=("EM" "BMA" "BO" "GS")
fi

if [ -z "$2" ]; then
  echo "Processing all available summary statistics..."
  input_dir=($(ls -d data/gwas/* | xargs -n 1 basename))
else
  echo "Processing summary statistics in $2 ..."
  input_dir=($2)
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

    echo "Submitting jobs for model $model_name..."

    for indir in "${input_dir[@]}"
    do

      rm -rf "./log/model_fit/$ld_panel/$model_name/$indir" || true
      mkdir -p "./log/model_fit/$ld_panel/$model_name/$indir"

      for ss_file in data/gwas/"$indir"/*/*.linear
      do
        if [ -e "$ss_file" ]; then
          sbatch -J "$ld_panel/$model_name/$indir" model_fit/model_fit_job.sh "$ss_file" "$m" "$ld_panel" "$fm"
        else
          echo "File $ss_file does not exist!"
        fi
      done
    done
  done
done
