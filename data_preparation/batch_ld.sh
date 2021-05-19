#!/bin/bash

rm -rf ./log/data_preparation/ld_mat/*.out || true
mkdir -p ./log/data_preparation/ld_mat/

echo "Submitting jobs for computing LD matrices with the windowed estimator..."

for c in $(seq 1 22)
do
  sbatch data_preparation/ld_matrix_job.sh "windowed" "$c"
done

echo "Submitting jobs for computing LD matrices with the shrinkage estimator..."

for c in $(seq 1 22)
do
  sbatch data_preparation/ld_matrix_job.sh "shrinkage" "$c"
done