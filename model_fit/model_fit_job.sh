#!/bin/bash
#SBATCH --account=def-sgravel
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=2GB
#SBATCH --time=02:00:00
#SBATCH --output=./log/model_fit/%x.out
#SBATCH --mail-user=shadi.zabad@mail.mcgill.ca
#SBATCH --mail-type=FAIL

echo "Job started at: `date`"

source "$HOME/pyenv/bin/activate"

model=${2:-"VIPRS"}
ld_panel=${3-"ukbb_50k_windowed"}
fitting_method=${4-"EM"}

echo "Performing model fit..."
echo "Dataset: $1"
echo "Model: $model"
echo "LD Panel: $ld_panel"

SECONDS=0

python model_fit/fit_prs.py -s "$1" -m "$model" -l "$ld_panel" -f "$fitting_method"

MINUTES=$(echo "scale=2; $SECONDS/60" | bc)

echo "Job finished with exit code $? at: `date`"
echo "Duration (minutes): $MINUTES"
