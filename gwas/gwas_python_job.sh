#!/bin/bash
#SBATCH --account=def-sgravel
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=8GB
#SBATCH --time=02:00:00
#SBATCH --output=./log/gwas/%x.out
#SBATCH --mail-user=shadi.zabad@mail.mcgill.ca
#SBATCH --mail-type=FAIL

echo "Job started at: `date`"
echo "Job ID: $SLURM_JOBID"

source "$HOME/pyenv/bin/activate"

pheno_file=$1  # The input file path
keep_file=${2:-"data/keep_files/ukbb_train_subset.keep"}
output_dir=$3
standardize=${4:-1}  # Whether to standardize the genotype/phenotype before performing regression (default: TRUE)


echo "Performing regression on phenotypes in: $pheno_file"
echo "with SNPs on chromosome: $chr..."

echo "Analysis started at: `date`"

for chr in $(seq 1 22)
do
  python gwas/python_gwas.py -p "$pheno_file" -c "$chr" -s "$standardize" -k "$keep_file" -o "$output_dir"
done

echo "Job finished with exit code $? at: `date`"
