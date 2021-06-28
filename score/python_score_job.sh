#!/bin/bash
#SBATCH --account=def-sgravel
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=8GB
#SBATCH --time=00:30:00
#SBATCH --output=./log/score/%x/%j.out
#SBATCH --mail-user=shadi.zabad@mail.mcgill.ca
#SBATCH --mail-type=FAIL

source "$HOME/pyenv/bin/activate"

echo "Generating polygenic scores for model fit: $1..."

python score/generate_scores.py -f "$1"

echo "Job finished with exit code $? at: `date`"
