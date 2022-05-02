#!/bin/bash
#SBATCH --account=def-sgravel
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=2GB
#SBATCH --time=05:00:00
#SBATCH --output=./log/score_minority/%x.out
#SBATCH --mail-user=shadi.zabad@mail.mcgill.ca
#SBATCH --mail-type=FAIL

echo "Job started at: `date`"
echo "Job ID: $SLURM_JOBID"

module load plink
source "$HOME/pyenv/bin/activate"

echo "Generating polygenic scores for model fit: $1..."

for f in data/model_fit/"$1"/*/real_fold_*/*
do
  echo "Processing: $f"
  python score/generate_scores.py -f "$f" \
                                  --bed-dir "data/ukbb_qc_genotypes_minority" \
                                  --keep-file "data/keep_files/ukbb_qc_individuals_minority.keep" \
                                  --prefix "minority"
done

echo "Job finished with exit code $? at: `date`"
