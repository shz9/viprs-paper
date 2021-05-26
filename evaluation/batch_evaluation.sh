#!/bin/bash

rm -rf ./log/evaluation/*.out || true
mkdir -p ./log/evaluation/

echo "Submitting jobs for model evaluation..."

ld_panels=("ukbb_windowed" "ukbb_shrinkage" "ukbb_sample")

for ld in "${ld_panels[@]}"
do
  for trait_f in data/simulated_phenotypes/*/*.txt
  do
    sbatch evaluation/evaluation_job.sh "$trait_f" "$ld"
  done
done
