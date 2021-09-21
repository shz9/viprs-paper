#!/bin/bash
#SBATCH --account=def-sgravel
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=2GB
#SBATCH --time=02:00:00
#SBATCH --output=./log/model_fit/%x.out
#SBATCH --mail-user=shadi.zabad@mail.mcgill.ca
#SBATCH --mail-type=FAIL

echo "Job started at: `date`"
echo "Job ID: $SLURM_JOBID"

model=${2:-"VIPRS"}
ld_panel=${3-"ukbb_50k_windowed"}
fitting_method=${4-"EM"}
genomewide=${5-false}
local_grid=${6-false}
grid_metric=${7-"ELBO"}

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

if [ "$genomewide" = true ]; then
  if [ "$local_grid" = true ]; then
    python model_fit/fit_prs.py -s "$1" -m "$model" -l "$ld_panel" -f "$fitting_method" --grid-metric "$grid_metric" --local-grid --genomewide
  else
    python model_fit/fit_prs.py -s "$1" -m "$model" -l "$ld_panel" -f "$fitting_method" --grid-metric "$grid_metric" --genomewide
  fi
else
  if [ "$local_grid" = true ]; then
    python model_fit/fit_prs.py -s "$1" -m "$model" -l "$ld_panel" -f "$fitting_method" --grid-metric "$grid_metric" --local-grid
  else
    python model_fit/fit_prs.py -s "$1" -m "$model" -l "$ld_panel" -f "$fitting_method" --grid-metric "$grid_metric"
  fi
fi

MINUTES=$(echo "scale=2; $SECONDS/60" | bc)

echo "Job finished with exit code $? at: `date`"
echo "Duration (minutes): $MINUTES"
