#!/bin/bash
#SBATCH --account=def-sgravel
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=4GB
#SBATCH --time=00:30:00
#SBATCH --output=./log/model_fit/%x/%j.out
#SBATCH --mail-user=shadi.zabad@mail.mcgill.ca
#SBATCH --mail-type=FAIL

echo "Job started at: `date`"

gctb_bin="$HOME/projects/def-sgravel/bin/gctb_v2.03/gctb"

# Inputs:
ss_file=$1 # Summary statistics file
ld_mat=$2  # LD matrix file
chrom=$3   # Chromosome number

ss_dir=$(dirname $ss_file)
trait=$(basename "$ss_dir")
config_dir=$(dirname $ss_dir)
config=$(basename "$config_dir")

mkdir -p "data/model_fit/external/SBayesR/$config/$trait/"

SECONDS=0

$gctb_bin --sbayes R \
         --ldm "$ld_mat" \
         --pi 0.95,0.02,0.02,0.01 \
         --gamma 0.0,0.01,0.1,1 \
         --gwas-summary "$ss_file" \
         --chain-length 10000 \
         --burn-in 2000 \
         --out-freq 100 \
         --out "data/model_fit/external/SBayesR/$config/$trait/chr_$chrom"

MINUTES=$(echo "scale=2; $SECONDS/60" | bc)

echo "Transforming output of SBayesR..."

source "$HOME/pyenv/bin/activate"
python external/SBayesR/transform_output.py "data/model_fit/external/SBayesR/$config/$trait/chr_$chrom"

echo "Job finished with exit code $? at: `date`"
echo "Duration (minutes): $MINUTES"
