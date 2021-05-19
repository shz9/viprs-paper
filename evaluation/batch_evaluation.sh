#!/bin/bash

rm -rf ./log/evaluation/*.out || true
mkdir -p ./log/evaluation/

echo "Submitting jobs for model evaluation..."

for trait_f in data/simulated_phenotypes/*/*.txt
do
  sbatch evaluation/evaluation_job.sh "$trait_f"
done
