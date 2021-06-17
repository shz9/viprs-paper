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

module load plink

echo "Creating a combined .mindrem.id file..."
# Combine the IDs of filtered individuals from all chromosomes:
awk '(NR == 1) || (FNR > 1)' data/ukbb_qc_genotypes/*.mindrem.id > data/ukbb_qc_genotypes/combined.mindrem.id

echo "Filtering individuals with excessive missingness from all chromosomes..."

for chr in $(seq 1 22)
do
  plink --bfile "data/ukbb_qc_genotypes/chr_$chr" \
        --remove data/ukbb_qc_genotypes/combined.mindrem.id \
        --out "data/ukbb_qc_genotypes/chr_$chr"
done

rm -r data/ukbb_qc_genotypes/*~

echo "Job finished with exit code $? at: `date`"
