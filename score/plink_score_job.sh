#!/bin/bash
#SBATCH --account=def-sgravel
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=4GB
#SBATCH --time=00:10:00
#SBATCH --output=./log/score/%x/%j.out
#SBATCH --mail-user=shadi.zabad@mail.mcgill.ca
#SBATCH --mail-type=FAIL

module load plink

fit_file=$1
chrom=$(basename "$fit_file" .fit)
file_dirname=$(dirname $fit_file)
output_dir="${file_dirname/model_fit/test_scores}"

mkdir -p "$output_dir"

plink2 --bfile data/ukbb_qc_genotypes/"$chrom" \
       --keep data/keep_files/ukbb_test_subset.keep \
       --score "$fit_file" 2 4 6 header-read variance-standardize \
       --out "$output_dir/$chrom"

echo "Transforming PLINK scores to standard format..."
# PLINK computes an average across variants. Transform it to PRS:
awk -v FS='\t' -v OFS='\t' '{ print $1, $2, $3 * $5 }' "$output_dir/$chrom".sscore > "$output_dir/$chrom".prs

# Update the header:
sed -i '1s/.*/FID\tIID\tPRS/' "$output_dir/$chrom".pprs

rm "$output_dir/$chrom".sscore

echo "Job finished with exit code $? at: `date`"