#!/bin/bash
#SBATCH --account=def-sgravel
#SBATCH --cpus-per-task=16
#SBATCH --mem-per-cpu=8GB
#SBATCH --time=1:00:00
#SBATCH --output=./log/data_preparation/ld_mat/%j.out
#SBATCH --mail-user=shadi.zabad@mail.mcgill.ca
#SBATCH --mail-type=FAIL

source "$HOME/pyenv/bin/activate"

LD_EST=${1:-"windowed"}  # LD estimator (default "windowed")
CHR=${2:-22}  # Chromosome number (default 22)

echo "Computing the LD matrix for chromosome $CHR using the $LD_EST estimator..."

python data_preparation/compute_ld_matrices.py --estimator "$LD_EST" --chr "$CHR"

echo "Job finished with exit code $? at: `date`"
