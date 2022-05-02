#!/bin/bash

for c in $(seq 1 22)
do
  source multi_pop_analysis/data_preparation/ukbb_qc_job.sh "$c"
done
