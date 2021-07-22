#!/bin/bash

rm -rf ./log/simulation/ || true
mkdir -p ./log/simulation/

echo "Submitting jobs for performing phenotype simulation..."

h2g=(0.1 0.3 0.5)  # Heritability values
pc=(0.0001 0.001 0.01)  # Proportion of causal SNPs
n_replicates=10

for h in "${h2g[@]}"
do
  for p in "${pc[@]}"
  do
    for r in $(seq 1 $n_replicates)
    do
      sbatch simulation/submit_sim_job.sh "$h" "$p" "$r"
    done
  done
done
