#!/bin/bash

ld_estimator=${1:-"windowed"}

echo "Submitting jobs for computing LD matrices from UKBB with the $ld_estimator estimator..."

for kf in data/keep_files/ukbb_ld_*_subset.keep
do
  sample_size=$(awk -F_ '{print $4}' <<< "$kf")
  echo "Using a sample size of $sample_size"

  rm -rf ./log/data_preparation/ld_mat/"ukbb_$sample_size/$ld_estimator" || true
  mkdir -p ./log/data_preparation/ld_mat/"ukbb_$sample_size/$ld_estimator"

  for c in $(seq 1 22)
  do
    sbatch -J "ukbb_$sample_size/$ld_estimator/chr_$c" \
            data_preparation/compute_ld_new.sh "$ld_estimator" "data/ukbb_qc_genotypes/chr_$c" "ukbb_$sample_size" "$kf"
  done
done
