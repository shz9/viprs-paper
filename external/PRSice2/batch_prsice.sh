#!/bin/bash

echo "Fitting PRSice2 to summary statistics..."

if [ -z "$1" ]; then
  echo "Processing all available summary statistics..."
  input_dir=($(ls -d data/gwas/* | xargs -n 1 basename))
else
  echo "Processing summary statistics in $1 ..."
  input_dir=($1)
fi

for indir in "${input_dir[@]}"
do

  rm -rf "./log/model_fit/external/PRSice2/$indir" || true
  mkdir -p "./log/model_fit/external/PRSice2/$indir"

  for ss_file in data/gwas/"$indir"/*/*.linear
  do
    if [ -e "$ss_file" ]; then
      chrom=$(basename "$ss_file" | cut -d. -f1 | cut -d "_" -f 2)
      sbatch -J "external/PRSice2/$indir" external/PRSice2/fit_prsice.sh "$ss_file" "$chrom"
    else
      echo "File $ss_file does not exist!"
    fi
  done
done
