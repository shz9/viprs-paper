#!/bin/bash

rm -rf ./log/simulation/*.out || true
mkdir -p ./log/simulation/

echo "Submitting jobs for performing phenotype simulation..."

h2g=(0.1 0.3 0.5)  # Heritability values
pc=(0.001 0.01 0.1)  # Proportion of causal SNPs
n_replicates=10

for h in "${h2g[@]}"
do
   for p in "${pc[@]}"
   do
     sbatch simulation/submit_sim_job.sh "$h" "$p" "$n_replicates"
   done
done
