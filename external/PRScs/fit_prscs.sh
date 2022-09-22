#!/bin/bash
#SBATCH --account=def-sgravel
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=2GB
#SBATCH --time=08:00:00
#SBATCH --output=./log/model_fit/%x.out
#SBATCH --mail-user=shadi.zabad@mail.mcgill.ca
#SBATCH --mail-type=FAIL

echo "Job started at: `date`"
echo "Job ID: $SLURM_JOBID"

echo "Performing model fit..."
echo "Dataset: $1"
echo "Model: PRScs"

source "$HOME/pyenv/bin/activate"
prscs_bin="external/PRScs/bin/PRScs/PRScs.py"

export MKL_NUM_THREADS=8
export NUMEXPR_NUM_THREADS=8
export OMP_NUM_THREADS=8

# Read configs (e.g. LD matrix path):
. external/PRScs/config.sh

# Inputs:
ss_dir=$(readlink -e "$1") # Summary statistics directory

trait=$(basename "$ss_dir")
config_dir=$(dirname "$ss_dir")
config=$(basename "$config_dir")
trait_type=$(basename $(dirname "$config_dir")) # The regression type (binary/quantitative)

if [[ $config == *"real"* ]]; then
  fold_name="${config/real_/}"
  N=$(wc -l < "data/keep_files/ukbb_cv/$trait_type/$trait/$fold_name/train.keep")
else
  N=$(wc -l < "data/keep_files/ukbb_train_subset.keep")
fi

output_dir="data/model_fit/external/PRScs/$trait_type/$config/$trait"

mkdir -p "$output_dir"

SECONDS=0

for chrom in $(seq 1 22)
do
  python "$prscs_bin" --ref_dir "$LD_PANEL_PATH" \
         --bim_prefix "data/ukbb_qc_genotypes/chr_$chrom" \
         --sst_file "$ss_dir/chr_${chrom}.prscs.ss" \
         --out_dir "$output_dir/chr_$chrom" \
         --n_gwas "$N" \
         --chrom "$chrom"
done

MINUTES=$(echo "scale=2; $SECONDS/60" | bc)

echo "Transforming output of PRScs..."

python external/PRScs/transform_output.py -o "$output_dir"
python model_fit/combine_fit_files.py -d "data/model_fit/$SLURM_JOB_NAME"

echo "Job finished with exit code $? at: `date`"
echo "Duration (minutes): $MINUTES"
