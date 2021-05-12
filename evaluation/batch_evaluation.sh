#!/bin/bash

for trait_f in data/simulated_phenotypes/*/*.txt
do
  sbatch evaluation/evaluation_job.sh "$trait_f"
done
