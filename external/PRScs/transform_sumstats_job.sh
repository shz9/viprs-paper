#!/bin/bash
#SBATCH --account=def-sgravel
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=2GB
#SBATCH --time=00:15:00
#SBATCH --output=./log/PRScs/sumstats_transform.out
#SBATCH --mail-user=shadi.zabad@mail.mcgill.ca
#SBATCH --mail-type=FAIL

source "$HOME/pyenv/bin/activate"

echo "Transforming summary statistics to the PRScs format..."
echo "Start time: `date`"

find data/gwas/*/*/*/ -type f -name *.PHENO1.glm.* | xargs -I @ -P 7 python external/PRScs/transform_sumstats.py -s "@" -t "plink"

echo "Job finished with exit code $? at: `date`"
