#!/bin/bash
#SBATCH --account=ctb-sgravel
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=2GB
#SBATCH --time=01:00:00
#SBATCH --output=./log/simulation_supplementary/%x/%j.out
#SBATCH --mail-user=shadi.zabad@mail.mcgill.ca
#SBATCH --mail-type=FAIL

echo "Job started at: `date`"
echo "Job ID: $SLURM_JOBID"

source "$HOME/viprs_env_test/bin/activate"
module load plink

H2G=${1}  # Heritability
MODEL=${2}  # Model
REP=${3:-1}  # Replicate number
TYPE=${4:-"quantitative"}

echo "Performing phenotype simulation using the following configurations:"
echo "Heritability: $H2G"
echo "Model: $MODEL"
echo "Replicate number: $REP"
echo "Type: $TYPE"

# Parse optional parameters:
opt_params=()

if [ "${MODEL}" == "sparseGM" ]; then
  opt_params+=(--mix-prop "0.95,0.02,0.02,0.01")
  opt_params+=(--var-mult "0.0,0.01,0.1,1")
fi

if [ "${MODEL}" == "infGM" ]; then
  opt_params+=(--mix-prop "0.95,0.02,0.02,0.01")
  opt_params+=(--var-mult "0.001,0.01,0.1,1")
fi

if [ "$TYPE" == "binary" ]; then
  likelihood="binomial"
else
  likelihood="gaussian"
fi


output_dir="data/phenotypes/$TYPE/h2_${H2G}_${MODEL}/"

mkdir -p "$output_dir"

magenpy_simulate --bed-files "data/ukbb_qc_genotypes/chr_*" \
                 --output-file "$output_dir/$REP" \
                 --temp-dir "${SLURM_TMPDIR:-temp}" \
                 --h2 "$H2G" \
                 --likelihood "$likelihood" \
                 --backend "plink" \
                 "${opt_params[@]}"

mv "$output_dir/${REP}.SimPheno" "$output_dir/${REP}.txt"

echo "Job finished with exit code $? at: `date`"
