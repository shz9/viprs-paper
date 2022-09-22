#!/bin/bash

pheno_type=${1:-"quantitative"}

rm -rf "./log/simulation_supplementary/$pheno_type" || true
mkdir -p "./log/simulation_supplementary/$pheno_type"

echo "Submitting jobs for performing phenotype simulation..."

h2g=(0.1 0.3 0.5)  # Heritability values
models=("inf" "sparseGM" "infGM")
n_replicates=10

for h in "${h2g[@]}"
do
  for m in "${models[@]}"
  do
    for r in $(seq 1 $n_replicates)
    do
      sbatch -J "$pheno_type" simulation_supplementary/submit_sim_job.sh "$h" "$m" "$r" "$pheno_type"
    done
  done
done
