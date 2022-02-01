#!/bin/bash
#SBATCH --account=ctb-sgravel
#SBATCH --cpus-per-task=12
#SBATCH --mem-per-cpu=4GB
#SBATCH --time=04:00:00
#SBATCH --output=./log_all/score/%x.out
#SBATCH --mail-user=shadi.zabad@mail.mcgill.ca
#SBATCH --mail-type=FAIL

echo "Job started at: `date`"
echo "Job ID: $SLURM_JOBID"

module load plink
source "$HOME/pyenv/bin/activate"

echo "Generating polygenic scores for model fit: $1..."

python analysis_10m_snps/score/generate_scores.py -f "$1"

echo "Job finished with exit code $? at: `date`"
