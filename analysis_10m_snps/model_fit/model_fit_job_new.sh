#!/bin/bash
#SBATCH --account=ctb-sgravel
#SBATCH --cpus-per-task=40
#SBATCH --mem-per-cpu=0
#SBATCH --time=10:00:00
#SBATCH --output=./log_all/model_fit/%x.out
#SBATCH --mail-user=shadi.zabad@mail.mcgill.ca
#SBATCH --mail-type=FAIL

echo "Job started at: `date`"
echo "Job ID: $SLURM_JOBID"

ss_dir=$(readlink -e "$1")  # Summary statistics directory
model=${2:-"VIPRS"}
chromosome=${3-"22"}
fitting_method=${4-"EM"}
local_grid=${5-false}
grid_metric=${6-"ELBO"}
opt_params=${7}

source "$HOME/viprs_annealed_env/bin/activate"
module load plink

export MKL_NUM_THREADS=8
export NUMEXPR_NUM_THREADS=8
export OMP_NUM_THREADS=8

echo "Performing model fit..."
echo "Dataset: $1"
echo "Model: $model"
echo "Fitting strategy: $fitting_method"

trait=$(basename "$ss_dir")
config_dir=$(dirname "$ss_dir")
config=$(basename "$config_dir")
trait_type=$(basename $(dirname "$config_dir")) # The regression type (binary/quantitative)
pheno_config="${config/_fold_*/}"

# Parse optional parameters:
extra_params=()

if [ "$genomewide" = true ]; then
  extra_params+=(--genomewide)
fi

if [ "$local_grid" = true ]; then
  extra_params+=(--h2-informed-grid)
fi

if [ "$grid_metric" = "validation" ] || [ "$grid_metric" = "pseudo_validation" ]; then
  extra_params+=(--validation-bed "data_all/ukbb_qc_genotypes/chr_*.bed")
  extra_params+=(--validation-pheno "data/phenotypes/$trait_type/$pheno_config/$trait.txt")

  if [[ $config == *"real"* ]]; then
    extra_params+=(--validation-keep "data/keep_files/ukbb_cv/${trait_type}/${trait}/${config#"real_"}/validation.keep")
  else
    extra_params+=(--validation-keep "data/keep_files/ukbb_valid_subset.keep")
  fi

fi

SECONDS=0

viprs_fit -l "data_all/ld/ukbb_all_windowed/ld/" \
         -s "$ss_dir/chr_${chromosome}.PHENO*" \
         --sumstats-format "plink" \
         --model "$model" \
         --hyp-search "$fitting_method" \
         --grid-metric "$grid_metric" \
         --opt-params "$opt_params" \
         --pi-steps 30 \
         --output-file "data_all/model_fit/$SLURM_JOB_NAME" \
         --backend "plink" \
         --compress \
         "${extra_params[@]}"

MINUTES=$(echo "scale=2; $SECONDS/60" | bc)

echo "Job finished with exit code $? at: `date`"
echo "Duration (minutes): $MINUTES"
