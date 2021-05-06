#!/bin/bash

echo "Submitting QC jobs..."

for c in $(seq 1 22)
do
  sbatch data_preparation/qc_job.sh "$c"
done

