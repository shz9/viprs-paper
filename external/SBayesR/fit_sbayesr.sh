#!/bin/bash
#SBATCH --account=def-sgravel
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=2GB
#SBATCH --time=04:00:00
#SBATCH --output=./log/model_fit/%x.out
#SBATCH --mail-user=shadi.zabad@mail.mcgill.ca
#SBATCH --mail-type=FAIL

echo "Job started at: `date`"
echo "Job ID: $SLURM_JOBID"

echo "Performing model fit..."
echo "Dataset: $1"
echo "Model: SBayesR"

gctb_bin="external/SBayesR/gctb_v2.03/gctb"

export MKL_NUM_THREADS=8
export NUMEXPR_NUM_THREADS=8
export OMP_NUM_THREADS=8

# Read configs (e.g. LD matrix path):
. external/SBayesR/config.sh

# Inputs:
ss_dir=$(readlink -e "$1") # Summary statistics directory

trait=$(basename "$ss_dir")
config_dir=$(dirname "$ss_dir")
config=$(basename "$config_dir")
trait_type=$(basename $(dirname "$config_dir")) # The regression type (binary/quantitative)

output_dir="data/model_fit/external/SBayesR/$trait_type/$config/$trait"

mkdir -p "$output_dir"

SECONDS=0

for chrom in $(seq 1 22)
do
  $gctb_bin --sbayes R \
           --ldm "$LD_PANEL_PATH/ukbEURu_hm3_chr${chrom}_v3_50k.ldm.sparse" \
           --pi 0.95,0.02,0.02,0.01 \
           --gamma 0.0,0.01,0.1,1 \
           --gwas-summary "$ss_dir/chr_${chrom}.ma" \
           --unscale-genotype \
           --chain-length "$CHAIN_LENGTH" \
           --burn-in "$BURN_IN" \
           --out-freq "$OUT_FREQ" \
           --out "$output_dir/chr_$chrom"
done

MINUTES=$(echo "scale=2; $SECONDS/60" | bc)

echo "Transforming output of SBayesR..."

source "$HOME/pyenv/bin/activate"
python external/SBayesR/transform_output.py -o "$output_dir" -s "$ss_dir"

echo "Job finished with exit code $? at: `date`"
echo "Duration (minutes): $MINUTES"
