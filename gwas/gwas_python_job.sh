#!/bin/bash
#SBATCH --account=def-sgravel
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=4GB
#SBATCH --time=01:00:00
#SBATCH --output=./log/gwas/%j.out
#SBATCH --mail-user=shadi.zabad@mail.mcgill.ca
#SBATCH --mail-type=FAIL

source "$HOME/pyenv/bin/activate"

python gwas/python_gwas.py "$1"

echo "Job finished with exit code $? at: `date`"
