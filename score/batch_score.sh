#!/bin/bash

ld_panel=${1:-"ukbb_50k_windowed"}

echo "Submitting jobs for generating per-chromosome polygenic scores."
echo "Processing data for models using $ld_panel LD panel..."

if [ -z "$2" ]; then
  echo "Generating polygenic scores for all configurations..."
  input_dir=($(ls -d data/gwas/* | xargs -n 1 basename))
else
  echo "Generating polygenic scores for phenotypes in $2 ..."
  input_dir=($2)
fi

for indir in "${input_dir[@]}"
do

  rm -rf "./log/score/$ld_panel/$indir" || true
  mkdir -p "./log/score/$ld_panel/$indir"

  for fit_file in data/model_fit/"$ld_panel"/*/"$indir"/*/*.fit
  do
    sbatch -J "$ld_panel/$indir" evaluation/evaluation_job.sh "$fit_file"
  done

done
