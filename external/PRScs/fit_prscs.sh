#!/bin/bash
#SBATCH --account=def-sgravel
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=2GB
#SBATCH --time=08:00:00
#SBATCH --output=./log/model_fit/%x.out
#SBATCH --mail-user=shadi.zabad@mail.mcgill.ca
#SBATCH --mail-type=FAIL

echo "Job started at: `date`"
echo "Performing model fit..."
echo "Dataset: $1"
echo "Model: PRScs"

source "$HOME/pyenv/bin/activate"
prscs_bin="$HOME/projects/def-sgravel/bin/PRScs/PRScs.py"

# Inputs:
ss_dir=$(readlink -e "$1") # Summary statistics directory

trait=$(basename "$ss_dir")
config=$(basename "$(dirname "$ss_dir")")

if [[ $config == *"real"* ]]; then
  fold_name="${config/real_/}"
  N=$(wc -l < "data/keep_files/ukbb_cv/$trait/$fold_name/train.keep")
else
  N=$(wc -l < "data/keep_files/ukbb_train_subset.keep")
fi

output_dir="data/model_fit/external/PRScs/$config/$trait"

mkdir -p "$output_dir"

SECONDS=0

for chrom in $(seq 1 22)
do
  python "$prscs_bin" --ref_dir "$HOME/projects/def-sgravel/data/ld/ldblk_ukbb_eur" \
         --bim_prefix "data/ukbb_qc_genotypes/chr_$chrom" \
         --sst_file "$ss_dir/chr_${chrom}.prscs.ss" \
         --out_dir "$output_dir/chr_$chrom" \
         --n_gwas "$N" \
         --chrom "$chrom"
done

MINUTES=$(echo "scale=2; $SECONDS/60" | bc)

echo "Transforming output of PRScs..."

python external/PRScs/transform_output.py -o "$output_dir"

echo "Job finished with exit code $? at: `date`"
echo "Duration (minutes): $MINUTES"
