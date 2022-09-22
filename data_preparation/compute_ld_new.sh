#!/bin/bash
#SBATCH --account=ctb-sgravel
#SBATCH --cpus-per-task=16
#SBATCH --mem-per-cpu=8GB
#SBATCH --time=2:00:00
#SBATCH --output=./log/data_preparation/ld_mat/%x.out
#SBATCH --mail-user=shadi.zabad@mail.mcgill.ca
#SBATCH --mail-type=FAIL

echo "Job started at: `date`"
echo "Job ID: $SLURM_JOBID"

. global_config.sh

source "$HOME/viprs_env_test/bin/activate"

LD_EST=${1:-"windowed"}  # LD estimator (default "windowed")
BEDFILE=${2:-"data/ukbb_qc_genotypes/chr_22"}  # Bed file (default 22)
NAME=${3:-"ukbb_50k"}
KEEPFILE=$4  # Keep file for individuals

echo "Computing the LD matrix $NAME for chromosome $(basename $BEDFILE) using the $LD_EST estimator..."

SECONDS=0

# Parse optional parameters:
opt_params=()

if [ "${LD_EST}" == "windowed" ]; then
  opt_params+=(--ld-window-cm 3.)
elif [ "${LD_EST}" == "block" ]; then
  opt_params+=(--ld-blocks "metadata/ldetect_blocks.txt")
elif [ "${LD_EST}" == "shrinkage" ]; then
  opt_params+=(--genmap-Ne 11400)
  opt_params+=(--genmap-sample-size 183)
  opt_params+=(--shrinkage-cutoff 0.001)
fi

if [ -n "$KEEPFILE" ]; then
  opt_params+=(--keep "$KEEPFILE")
fi

magenpy_ld --estimator "$LD_EST" \
           --bfile "$BEDFILE" \
           --min-mac "$MIN_MAC" \
           --min-maf "$MIN_MAF" \
           --temp-dir "${SLURM_TMPDIR:-temp}" \
           --output-dir "data/ld/${NAME}_${LD_EST}/" \
           --backend "plink" \
           "${opt_params[@]}"

MINUTES=$(echo "scale=2; $SECONDS/60" | bc)

echo "Job finished with exit code $? at: `date`"
echo "Duration (minutes): $MINUTES"