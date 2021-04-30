#!/bin/bash
#SBATCH --account=def-sgravel
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=1GB
#SBATCH --time=1:00:00
#SBATCH --mail-user=shadi.zabad@mail.mcgill.ca
#SBATCH --mail-type=ALL

source "$HOME/pyenv/bin/activate"

H2G=${1:-0.1}  # Heritability (default 0.1)
PC=${2:-0.01}  # Proportion of causal variants (default 0.01)
NREP=${3:-10}  # Number of replicates (default 10)

python simulation/simulate_phenotypes.py --h2g "$H2G" -p "$PC" -n "$NREP"

echo "Job finished with exit code $? at: `date`"
