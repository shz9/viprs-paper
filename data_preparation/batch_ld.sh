#!/bin/bash

ld_estimator=("windowed" "block" "shrinkage" "sample")

for ld in "${ld_estimator[@]}"
do
  echo "Submitting jobs for computing LD matrices from UKBB with the $ld estimator..."

  for kf in data/keep_files/ukbb_ld_*_subset.keep
  do
    sample_size=$(awk -F_ '{print $4}' <<< "$kf")
    echo "Using a sample size of $sample_size"

    rm -rf ./log/data_preparation/ld_mat/"ukbb_$sample_size/$ld_estimator" || true
    mkdir -p ./log/data_preparation/ld_mat/"ukbb_$sample_size/$ld_estimator"

    for c in $(seq 1 22)
    do
      if [ $sample_size == "50k" ]; then
        sbatch -J "ukbb_$sample_size/$ld_estimator" --mem-per-cpu "14GB" --time "01:30:00" \
                data_preparation/ld_compute_job.sh "$ld" "data/ukbb_qc_genotypes/chr_$c" "ukbb_$sample_size" "$kf"
      else
        sbatch -J "ukbb_$sample_size/$ld_estimator" \
                data_preparation/ld_compute_job.sh "$ld" "data/ukbb_qc_genotypes/chr_$c" "ukbb_$sample_size" "$kf"
      fi
    done
  done

  echo "Submitting jobs for computing LD matrices from 1000G with the $ld estimator..."

  rm -rf ./log/data_preparation/ld_mat/1000G/"$ld_estimator" || true
  mkdir -p ./log/data_preparation/ld_mat/1000G/"$ld_estimator"

  for c in $(seq 1 22)
  do
    sbatch -J "1000G/$ld_estimator" data_preparation/ld_compute_job.sh "$ld" "data/1000G_qc_genotypes/chr_$c" "1000G"
  done

done
