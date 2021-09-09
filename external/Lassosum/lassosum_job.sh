#!/bin/bash
#SBATCH --account=def-sgravel
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=2GB
#SBATCH --time=00:45:00
#SBATCH --output=./log/model_fit/%x.out
#SBATCH --mail-user=shadi.zabad@mail.mcgill.ca
#SBATCH --mail-type=FAIL

# -----------------------------------------

echo "Job started at: `date`"
echo "Performing model fit..."
echo "Dataset: $1"
echo "Model: Lassosum"

module load gcc/9.3.0 r/4.0.2
export R_LIBS=$HOME/projects/def-sgravel/R_environments/R_4.0.2/lassosum

Rscript external/Lassosum/fit_lassosum.R "$1" "plink"

echo "Job finished with exit code $? at: `date`"