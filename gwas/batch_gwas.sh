#!/bin/bash

rm -rf ./log/gwas/*.out || true
mkdir -p ./log/gwas/

gwas_software=${1:-"python"}

echo "Submitting jobs for performing GWAS with $gwas_software..."

for sim_config in data/simulated_phenotypes/*
do
  if [ "$gwas_software" == "plink" ]; then
    sbatch gwas/gwas_plink_job.sh "$sim_config"
  else
    sbatch gwas/gwas_python_job.sh "$sim_config"
  fi
done
