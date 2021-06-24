#!/bin/bash
#SBATCH --account=def-sgravel
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=4GB
#SBATCH --time=01:00:00
#SBATCH --output=./log/evaluation/%x/%j.out
#SBATCH --mail-user=shadi.zabad@mail.mcgill.ca
#SBATCH --mail-type=FAIL

source "$HOME/pyenv/bin/activate"

echo "Performing model evaluation on phenotype file: $1..."
echo "Using model fits obtained with LD panel $2"

python evaluation/evaluate_prs.py -p "$1" -l "$2"

echo "Job finished with exit code $? at: `date`"
