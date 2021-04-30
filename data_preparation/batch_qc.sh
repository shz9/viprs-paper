#!/bin/bash

echo "Submitting QC jobs..."

for c in $(seq 1 22)
do
  sbatch data_preparation/qc_job.sh "$c"
done

echo "Computing LD matrices with the windowed estimator..."

for c in $(seq 1 22)
do
  sbatch data_preparation/ld_matrix_job.sh "windowed" "$c"
done

echo "Computing LD matrices with the shrinkage estimator..."

for c in $(seq 1 22)
do
  sbatch data_preparation/ld_matrix_job.sh "shrinkage" "$c"
done

