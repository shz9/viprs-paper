#!/bin/bash
#SBATCH --account=ctb-sgravel
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=2GB
#SBATCH --time=02:00:00
#SBATCH --output=./log/model_fit/%x.out
#SBATCH --mail-user=shadi.zabad@mail.mcgill.ca
#SBATCH --mail-type=FAIL

echo "Job started at: `date`"
echo "Job ID: $SLURM_JOBID"

echo "Performing model fit..."
echo "Dataset: $1"
echo "Model: MegaPRS"

ldak_bin="external/MegaPRS/ldak5.2.linux"

export MKL_NUM_THREADS=8
export NUMEXPR_NUM_THREADS=8
export OMP_NUM_THREADS=8

# Read configs (e.g. LD matrix path):
. external/MegaPRS/config.sh

# Activate the python environment:
source "$HOME/pyenv/bin/activate"

# Inputs:
ss_dir=$(readlink -e "$1") # Summary statistics directory
validation_keep_file=$2

trait=$(basename "$ss_dir")
config_dir=$(dirname "$ss_dir")
config=$(basename "$config_dir")
trait_type=$(basename $(dirname "$config_dir")) # The regression type (binary/quantitative)
pheno_config="${config/_fold_*/}"

output_dir="data/model_fit/external/MegaPRS/$trait_type/$config/$trait"

mkdir -p "$output_dir"

SECONDS=0

# Parse optional parameters:
opt_params=()

# Estimate per-SNP heritability:
# Here, we are doing this step genome-wide to account for rare annotations in the
# BLD-LDAK model (in case the user is using that model):
(head -1 "$ss_dir/chr_1.megaprs.ss" && tail -n +2 -q "$ss_dir"/chr_*.megaprs.ss ) > "$output_dir/combined.megaprs.ss"
python external/MegaPRS/create_exclude_file.py -s "$output_dir/combined.megaprs.ss" -f "$TAG_FILE"

# If the exclude file is not empty, append to the list of arguments we pass to LDAK:
if [ -s "$output_dir/combined.exclude" ]; then
  opt_params+=(--exclude "$output_dir/combined.exclude")
fi

$ldak_bin --sum-hers "$output_dir/combined.gcta" \
          --summary "$output_dir/combined.megaprs.ss" \
          --tagfile "$TAG_FILE" \
          --matrix "$LD_MATRIX_FILE" \
          --check-sums NO \
          --max-threads 7 \
          "${opt_params[@]}"


for chrom in $(seq 1 22)
do

  chrom_keep="${SLURM_TMPDIR:-temp}/chr_$chrom.keep"

  tail -n +2 "$ss_dir/chr_${chrom}.megaprs.ss" | awk '{print $1}' > "$chrom_keep"

  # Fit MegaPRS model:
  $ldak_bin --mega-prs "$output_dir/chr_$chrom.val" \
            --model bayesr \
            --ind-hers "$output_dir/combined.gcta.ind.hers" \
            --summary "$ss_dir/chr_${chrom}.megaprs.ss" \
            --cors "$LD_PANEL_PATH/chr_$chrom" \
            --chr "$chrom" \
            --extract "$chrom_keep" \
            --skip-cv YES \
            --window-cm 1 \
            --max-threads 7 \
            "${opt_params[@]}"

  # Convert predictor names to rsID:
  # python external/MegaPRS/predictor_to_rsid.py -f "$output_dir/chr_$chrom.val.effects"

  # Pick best model using validation set:
  $ldak_bin --validate "$output_dir/chr_$chrom.val" \
            --scorefile "$output_dir/chr_$chrom.val.effects" \
            --bfile "data/ukbb_qc_genotypes/chr_${chrom}" \
            --keep "$validation_keep_file" \
            --pheno "data/phenotypes/$trait_type/$pheno_config/$trait.txt" \
            --max-threads 7

  rm "$chrom_keep"

done

MINUTES=$(echo "scale=2; $SECONDS/60" | bc)

echo "Transforming output of MegaPRS..."

python external/MegaPRS/transform_output.py -o "$output_dir"

# Delete all intermediate files:
find "$output_dir" -type f ! -name '*.fit' -delete

python model_fit/combine_fit_files.py -d "data/model_fit/$SLURM_JOB_NAME"

echo "Job finished with exit code $? at: `date`"
echo "Duration (minutes): $MINUTES"
