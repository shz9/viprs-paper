#!/bin/bash

ld_panel=${1:-"ukbb_50k_windowed"}

echo "Submitting jobs for model evaluation using $ld_panel LD panel..."

if [ -z "$2" ]; then
  echo "Evaluating performance on all phenotypes..."
  input_dir=($(ls -d data/gwas/* | xargs -n 1 basename))
else
  echo "Evaluating performance on phenotypes in $2 ..."
  input_dir=($2)
fi

for indir in "${input_dir[@]}"
do

  rm -rf "./log/evaluation/$ld_panel/$indir" || true
  mkdir -p "./log/evaluation/$ld_panel/$indir"

  for trait_f in data/phenotypes/"$indir"/*.txt
  do
    sbatch -J "$ld_panel/$indir" evaluation/evaluation_job.sh "$trait_f" "$ld_panel"
  done

done
