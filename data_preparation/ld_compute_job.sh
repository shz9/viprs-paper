#!/bin/bash
#SBATCH --account=def-sgravel
#SBATCH --cpus-per-task=16
#SBATCH --mem-per-cpu=8GB
#SBATCH --time=1:00:00
#SBATCH --output=./log/data_preparation/ld_mat/%j.out
#SBATCH --mail-user=shadi.zabad@mail.mcgill.ca
#SBATCH --mail-type=FAIL

SECONDS=0
echo "Job started at: `date`"

source "$HOME/pyenv/bin/activate"

LD_EST=${1:-"windowed"}  # LD estimator (default "windowed")
BEDFILE=${2:-"data/ukbb_qc_genotypes/chr_22"}  # Bed file (default 22)
NAME=${3:-"ukbb_windowed_50k"}
KEEPFILE=$4  # Keep file for individuals


echo "Computing the LD matrix $NAME for chromosome $CHR using the $LD_EST estimator..."

if [ -n "$KEEPFILE" ]; then
  python data_preparation/compute_ld_matrices.py --estimator "$LD_EST" \
                                                 --bfile "$BEDFILE" \
                                                 --keep-file "$KEEPFILE" \
                                                 --panel-name "$NAME"
else
  python data_preparation/compute_ld_matrices.py --estimator "$LD_EST" \
                                                 --bfile "$BEDFILE" \
                                                 --panel-name "$NAME"
fi

echo "Job finished with exit code $? at: `date`"
MINUTES=$(echo "scale=2; $SECONDS/60" | bc)
echo "Duration (minutes): $MINUTES"