#!/bin/bash

rm -rf ./log/gwas/*.out || true
mkdir -p ./log/gwas/

echo "Submitting jobs for performing GWAS with PLINK..."

for sim_config in data/simulated_phenotypes/*
do
  sbatch gwas/gwas_plink_job.sh "$sim_config"
done
