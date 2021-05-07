#!/bin/bash

models=("vem_c" "gibbs_c")

for m in "${models[@]}"
do
  for ss_file in data/gwas/*/*/*.linear
  do
    sbatch model_fit/model_fit_job.sh "$ss_file" "$m"
  done
done