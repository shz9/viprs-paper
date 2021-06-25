#!/bin/bash
#SBATCH --account=def-sgravel
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=8GB
#SBATCH --time=00:30:00
#SBATCH --output=./log/gwas/%x/%j.out
#SBATCH --mail-user=shadi.zabad@mail.mcgill.ca
#SBATCH --mail-type=FAIL

source "$HOME/pyenv/bin/activate"

chr=${1:-22}  # Chromosome

echo "Performing regression on phenotypes in: $2"
echo "with SNPs on chromosome: $chr..."

echo "Analysis started at: `date`"

python gwas/python_gwas.py -i "$2" -c "$chr"

echo "Job finished with exit code $? at: `date`"
