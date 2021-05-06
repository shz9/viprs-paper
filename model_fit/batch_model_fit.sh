#!/bin/bash

for ss_file in data/gwas/*/*/*.linear
do
  sbatch model_fit/model_fit_job.sh "$ss_file"
done