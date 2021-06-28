#!/bin/bash

ld_panel=${1:-"ukbb_50k_windowed"}
model=${2:-"VIPRS"}

echo "Submitting jobs for generating per-chromosome polygenic scores."
echo "Model: $model"
echo "LD panel: $ld_panel"

if [ -z "$3" ]; then
  echo "Generating polygenic scores for all configurations..."
  input_dir=($(ls -d data/gwas/* | xargs -n 1 basename))
else
  echo "Generating polygenic scores for phenotypes in $3 ..."
  input_dir=($3)
fi

for indir in "${input_dir[@]}"
do

  rm -rf "./log/score/$ld_panel/$model/$indir" || true
  mkdir -p "./log/score/$ld_panel/$model/$indir"

  for fit_file in data/model_fit/"$ld_panel"/"$model"/"$indir"/*/*.fit
  do
    sbatch -J "$ld_panel/$model/$indir" score/score_job.sh "$fit_file"
  done

done
