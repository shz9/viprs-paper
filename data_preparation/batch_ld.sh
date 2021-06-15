#!/bin/bash

rm -rf ./log/data_preparation/ld_mat/ || true
mkdir -p ./log/data_preparation/ld_mat/

ld_estimator=("windowed" "shrinkage" "sample")

for ld in "${ld_estimator[@]}"
do
  echo "Submitting jobs for computing LD matrices from UKBB with the $ld estimator..."

  for kf in data/keep_files/ukbb_ld_*_subset.keep
  do
    sample_size=$(awk -F_ '{print $4}' <<< "$kf")
    echo "Using a sample size of $sample_size"
    for c in $(seq 22 22)
    do
      sbatch data_preparation/ld_compute_job.sh "$ld" "data/ukbb_qc_genotypes/chr_$c" "ukbb_$sample_size" "$kf"
    done
  done

  echo "Submitting jobs for computing LD matrices from 1000G with $ld estimator..."

  for c in $(seq 22 22)
  do
    sbatch data_preparation/ld_compute_job.sh "$ld" "data/1000G_qc_genotypes/chr_$c" "1000G"
  done

done
