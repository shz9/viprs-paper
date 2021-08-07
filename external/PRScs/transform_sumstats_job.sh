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

for ss_file in data/gwas/*/*/*.linear
do
  echo "> Transforming summary statistics file: $ss_file"
  python external/PRScs/transform_sumstats.py -s "$ss_file" -t "plink"
done

echo "Job finished with exit code $? at: `date`"
