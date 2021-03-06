#!/bin/bash
#SBATCH --account=def-sgravel
#SBATCH --cpus-per-task=40
#SBATCH --mem=0
#SBATCH --time=20:00:00
#SBATCH --output=./log/model_fit/%x.out
#SBATCH --mail-user=shadi.zabad@mail.mcgill.ca
#SBATCH --mail-type=FAIL

# -----------------------------------------

echo "Job started at: `date`"
echo "Job ID: $SLURM_JOBID"

echo "Performing model fit..."
echo "Dataset: $1"
echo "Model: LDPred2-$2"

export MKL_NUM_THREADS=8
export NUMEXPR_NUM_THREADS=8
export OMP_NUM_THREADS=8

module load gcc/9.3.0 r/4.0.2
export R_LIBS=external/LDPred2/R_ldpred2_env

SECONDS=0

Rscript "external/LDPred2/fit_ldpred2_$2.R" "$1" "plink"

MINUTES=$(echo "scale=2; $SECONDS/60" | bc)

source "$HOME/pyenv/bin/activate"
python model_fit/combine_fit_files.py -d "data/model_fit/$SLURM_JOB_NAME"

echo "Job finished with exit code $? at: `date`"
echo "Duration (minutes): $MINUTES"
