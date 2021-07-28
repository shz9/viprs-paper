#!/bin/bash
#SBATCH --account=def-sgravel
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=4GB
#SBATCH --time=01:00:00
#SBATCH --output=./log/model_fit/%x.out
#SBATCH --mail-user=shadi.zabad@mail.mcgill.ca
#SBATCH --mail-type=FAIL

echo "Job started at: `date`"
echo "Performing model fit..."
echo "Dataset: $1"
echo "Model: SBayesR"

gctb_bin="$HOME/projects/def-sgravel/bin/gctb_v2.03/gctb"

# Inputs:
ss_dir=$(readlink -e "$1") # Summary statistics directory

trait=$(basename "$ss_dir")
config=$(basename "$(dirname "$ss_dir")")

output_dir="data/model_fit/external/SBayesR/$config/$trait"

mkdir -p "$output_dir"

SECONDS=0

for chrom in $(seq 1 22)
do
  $gctb_bin --sbayes R \
           --ldm "$HOME/projects/def-sgravel/data/ld/ukbEURu_hm3_shrunk_sparse/ukbEURu_hm3_chr${chrom}_v3_50k.ldm.sparse" \
           --pi 0.95,0.02,0.02,0.01 \
           --gamma 0.0,0.01,0.1,1 \
           --gwas-summary "$ss_dir/chr_${chrom}.ma" \
           --chain-length 10000 \
           --burn-in 2000 \
           --out-freq 100 \
           --out "$output_dir/chr_$chrom"
done

MINUTES=$(echo "scale=2; $SECONDS/60" | bc)

echo "Transforming output of SBayesR..."

source "$HOME/pyenv/bin/activate"
python external/SBayesR/transform_output.py -o "$output_dir" -s "$ss_dir"

echo "Job finished with exit code $? at: `date`"
echo "Duration (minutes): $MINUTES"
