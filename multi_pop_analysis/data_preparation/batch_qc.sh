#!/bin/bash

for c in $(seq 1 22)
do
  source data_preparation/ukbb_qc_job.sh "$c" "hm3" "data/keep_files/ukbb_qc_individuals_minority.keep" "data/ukbb_qc_genotypes_minority"
done

source data_preparation/harmonize_ukbb_genotypes.sh "data/ukbb_qc_genotypes_minority"
