#!/bin/bash

mkdir -p "./log/data_preparation_minority/qc/"

for c in $(seq 1 22)
do
  sbatch -J "chr_$c" multi_pop_analysis/data_preparation/ukbb_qc_job.sh "$c"
done
