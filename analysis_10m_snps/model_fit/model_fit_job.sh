#!/bin/bash
#SBATCH --account=ctb-sgravel
#SBATCH --cpus-per-task=40
#SBATCH --mem-per-cpu=0
#SBATCH --time=10:00:00
#SBATCH --output=./log_all/model_fit/%x.out
#SBATCH --mail-user=shadi.zabad@mail.mcgill.ca
#SBATCH --mail-type=FAIL

echo "Job started at: `date`"
echo "Job ID: $SLURM_JOBID"

model=${2:-"VIPRS"}
ld_panel=${3-"ukbb_all_windowed"}
fitting_method=${4-"EM"}
chrom=${5-"22"}

if [ "${fitting_method}" == "GS" ] || [ "${fitting_method}" == "BMA" ]; then
  source setup_python_environment.sh
else
  source "$HOME/pyenv/bin/activate"
fi

module load plink

export MKL_NUM_THREADS=8
export NUMEXPR_NUM_THREADS=8
export OMP_NUM_THREADS=8

echo "Performing model fit..."
echo "Dataset: $1"
echo "Model: $model"
echo "LD Panel: $ld_panel"
echo "Fitting strategy: $fitting_method"

SECONDS=0

python analysis_10m_snps/model_fit/fit_prs.py -s "$1" -m "$model" -l "$ld_panel" -f "$fitting_method" --chromosome "$chrom"

MINUTES=$(echo "scale=2; $SECONDS/60" | bc)

echo "Job finished with exit code $? at: `date`"
echo "Duration (minutes): $MINUTES"
