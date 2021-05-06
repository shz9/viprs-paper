#!/bin/bash
#SBATCH --account=def-sgravel
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=2GB
#SBATCH --time=01:00:00
#SBATCH --mail-user=shadi.zabad@mail.mcgill.ca
#SBATCH --mail-type=ALL

source "$HOME/pyenv/bin/activate"

python model_fit/fit_prs.py "$1"

echo "Job finished with exit code $? at: `date`"
