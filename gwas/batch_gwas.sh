#!/bin/bash

for sim_config in data/simulated_phenotypes/*
do
  sbatch gwas/gwas_plink_job.sh "$sim_config"
done
