#!/bin/bash
#SBATCH --account=def-sgravel
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=2GB
#SBATCH --time=00:45:00
#SBATCH --output=./log/simulation/%x/%j.out
#SBATCH --mail-user=shadi.zabad@mail.mcgill.ca
#SBATCH --mail-type=FAIL

echo "Job started at: `date`"
echo "Job ID: $SLURM_JOBID"

source "$HOME/pyenv/bin/activate"
module load plink

H2G=${1:-0.1}  # Heritability (default 0.1)
PC=${2:-0.01}  # Proportion of causal variants (default 0.01)
REP=${3:-1}  # Replicate number
TYPE=${4:-"quantitative"}

echo "Performing phenotype simulation using the following configurations:"
echo "Heritability: $H2G"
echo "Proportion of causal variants: $PC"
echo "Replicate number: $REP"
echo "Type: $TYPE"

python simulation/simulate_phenotypes.py --h2g "$H2G" -p "$PC" -r "$REP" -t "$TYPE"

echo "Job finished with exit code $? at: `date`"
