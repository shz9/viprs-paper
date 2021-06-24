#!/bin/bash

echo "Fitting SBayesR to summary statistics..."

if [ -z "$1" ]; then
  echo "Processing all available summary statistics..."
  input_dir=($(ls -d data/gwas/* | xargs -n 1 basename))
else
  echo "Processing summary statistics in $1 ..."
  input_dir=($1)
fi

for indir in "${input_dir[@]}"
do

  rm -rf "./log/model_fit/external/SBayesR/$indir" || true
  mkdir -p "./log/model_fit/external/SBayesR/$indir"

  for ss_file in data/gwas/"$indir"/*/*.ma
  do
    if [ -e "$ss_file" ]; then
      chrom=$(basename "$ss_file" | cut -d. -f1 | cut -d "_" -f 2)
      ldm="$HOME/projects/def-sgravel/data/ld/ukbEURu_hm3_shrunk_sparse/ukbEURu_hm3_chr${chrom}_v3_50k.ldm.sparse"
      sbatch -J "external/SBayesR/$indir" external/SBayesR/fit_sbayesr.sh "$ss_file" "$ldm" "$chrom"
    else
      echo "File $ss_file does not exist!"
    fi
  done
done
