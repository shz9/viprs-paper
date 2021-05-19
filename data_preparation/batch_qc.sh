#!/bin/bash

rm -rf ./log/data_preparation/qc/*.out || true
mkdir -p ./log/data_preparation/qc/

echo "Submitting QC jobs..."

for c in $(seq 1 22)
do
  sbatch data_preparation/qc_job.sh "$c"
done

