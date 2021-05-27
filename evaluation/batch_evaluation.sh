#!/bin/bash

ld_panel=${1:-"ukbb_windowed"}

rm -rf "./log/evaluation/$ld_panel/*.out" || true
mkdir -p "./log/evaluation/$ld_panel"

echo "Submitting jobs for model evaluation using $ld_panel LD panel..."

for trait_f in data/simulated_phenotypes/*/*.txt
do
  sbatch -J "$ld_panel" evaluation/evaluation_job.sh "$trait_f" "$ld_panel"
done
