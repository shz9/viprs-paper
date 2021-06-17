#!/bin/bash

rm -rf ./log/data_preparation/ukbb_qc/ || true
mkdir -p ./log/data_preparation/ukbb_qc/

rm -rf ./log/data_preparation/1000G_qc/ || true
mkdir -p ./log/data_preparation/1000G_qc/

echo "Submitting QC jobs..."

for c in $(seq 1 22)
do
  sbatch data_preparation/ukbb_qc_job.sh "$c"
  sbatch data_preparation/1000G_qc_job.sh "$c"
done

