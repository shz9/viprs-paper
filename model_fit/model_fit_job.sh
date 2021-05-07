#!/bin/bash
#SBATCH --account=def-sgravel
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=2GB
#SBATCH --time=01:00:00
#SBATCH --mail-user=shadi.zabad@mail.mcgill.ca
#SBATCH --mail-type=ALL

source "$HOME/pyenv/bin/activate"

model=${2:-"vem_c"}

python model_fit/fit_prs.py -s "$1" -m "$model"

echo "Job finished with exit code $? at: `date`"
