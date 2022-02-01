#!/bin/bash
#SBATCH --account=ctb-sgravel
#SBATCH --cpus-per-task=16
#SBATCH --mem=32GB
#SBATCH --time=40:00:00
#SBATCH --output=./log_all/data_preparation/ld/%x.log
#SBATCH --mail-user=shadi.zabad@mail.mcgill.ca
#SBATCH --mail-type=FAIL

echo "Job started at: `date`"
echo "Job ID: $SLURM_JOBID"

chrom=${1:-22}

module load plink
source "$HOME/pyenv/bin/activate"

SECONDS=0

python analysis_10m_snps/data_preparation/compute_ld_matrices.py -c "$chrom"

MINUTES=$(echo "scale=2; $SECONDS/60" | bc)

echo "Job finished with exit code $? at: `date`"
echo "Duration (minutes): $MINUTES"

