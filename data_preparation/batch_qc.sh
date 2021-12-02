#!/bin/bash

data_source=${1:-"ukbb"}
snp_set=${2:-"hm3"}

if [ $data_source == "ukbb" ]; then
  if [ $snp_set == "hm3" ]; then
    log_dir="ukbb_qc/hm3"
  else
    log_dir="ukbb_qc/all"
  fi
  qc_script="data_preparation/ukbb_qc_job.sh"
else
  if [ $snp_set == "hm3" ]; then
    log_dir="1000G_qc/hm3"
  else
    log_dir="1000G_qc/all"
  fi
  qc_script="data_preparation/1000G_qc_job.sh"
fi

rm -rf "./log/data_preparation/$log_dir" || true
mkdir -p "./log/data_preparation/$log_dir"

echo "Submitting QC jobs..."

for c in $(seq 1 22)
do
  sbatch -J "$log_dir" "$qc_script" "$c" "$snp_set"
done
