#!/bin/bash
#SBATCH --account=def-sgravel
#SBATCH --cpus-per-task=16
#SBATCH --mem-per-cpu=8GB
#SBATCH --time=00:30:00
#SBATCH --output=./log/data_preparation/ukbb_qc/%j.out
#SBATCH --mail-user=shadi.zabad@mail.mcgill.ca
#SBATCH --mail-type=FAIL

# This script harmonizes the genotype data by keeping
# the same sets of individuals in all chromosomes.
# This is mainly to correct for the effect of filtering individuals
# with excessive missingness rates.

. global_config.sh

input_dir=${1:-"data/ukbb_qc_genotypes"}  # Chromosome number (default 22)

module load plink

echo "Creating a combined .mindrem.id file..."
# Combine the IDs of filtered individuals from all chromosomes:
rm -rf "$input_dir/combined.mindrem.id" || true
awk '(NR == 1) || (FNR > 1)' "$input_dir"/*.mindrem.id > "$input_dir/combined.mindrem.id"

echo "Filtering individuals with excessive missingness from all chromosomes..."

for chr in $(seq 1 22)
do
  echo "------- Filtering individuals from chromosome $chr... -------"
  plink2 --bfile "$input_dir/chr_$chr" \
         --make-bed \
         --mac "$MIN_MAC" \
         --maf "$MIN_MAF" \
         --max-maf "$MAX_MAF" \
         --remove "$input_dir/combined.mindrem.id" \
         --out "$input_dir/chr_$chr"
done

rm -r "$input_dir"/*~ || true

echo "Job finished with exit code $? at: `date`"
