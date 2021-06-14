#!/bin/bash

gwas_software=${1:-"python"}

rm -rf "./log/gwas/$gwas_software/" || true
mkdir -p "./log/gwas/$gwas_software"

echo "Submitting jobs for performing GWAS with $gwas_software..."

for sim_config in data/simulated_phenotypes/*
do
  if [ "$gwas_software" == "plink" ]; then
    sbatch -J "plink" gwas/gwas_plink_job.sh "$sim_config"
  else
    sbatch -J "python" gwas/gwas_python_job.sh "$sim_config"
  fi
done
