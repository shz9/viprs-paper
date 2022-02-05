#!/bin/bash
#SBATCH --account=def-sgravel
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=2GB
#SBATCH --time=01:00:00
#SBATCH --output=./log/model_fit/%x.out
#SBATCH --mail-user=shadi.zabad@mail.mcgill.ca
#SBATCH --mail-type=FAIL

echo "Job started at: `date`"
echo "Job ID: $SLURM_JOBID"

echo "Performing model fit..."
echo "Dataset: $1"
echo "Model: PRSice2"

export MKL_NUM_THREADS=8
export NUMEXPR_NUM_THREADS=8
export OMP_NUM_THREADS=8

module load gcc/9.3.0 r/4.0.2
export R_LIBS="external/PRSice2/R_PRSice2_env"

PRSiceHome="external/PRSice2/PRSice_v2.3.5"

# Inputs:
ss_dir=$(readlink -e "$1")  # Summary statistics directory
keep_file=$2   # Individual keep file for samples in the validation set
sumstats_type=${3:-"plink"}

trait=$(basename "$ss_dir")
config_dir=$(dirname "$ss_dir")
config=$(basename "$config_dir")
trait_type=$(basename $(dirname "$config_dir")) # The regression type (binary/quantitative)
pheno_config="${config/_fold_*/}"

output_dir="data/model_fit/external/PRSice2/$trait_type/$config/$trait/"

mkdir -p "$output_dir"

if [ "$sumstats_type" == "plink" ]; then
  p_pval="P"
  p_snp="ID"
else
  p_pval="PVAL"
  p_snp="SNP"
fi

if [ "${trait_type}" == "binary" ]; then
  reg_type="logistic"
  binary_target="T"
else
  reg_type="linear"
  binary_target="F"
fi

SECONDS=0

for chrom in $(seq 1 22)
do
  Rscript "$PRSiceHome/PRSice.R" \
          --dir "$R_LIBS" \
          --prsice "$PRSiceHome/PRSice_linux" \
          --base "$ss_dir/chr_${chrom}.PHENO1.glm.${reg_type}" \
          --ld "data/ukbb_qc_genotypes/chr_${chrom}" \
          --ld-keep "data/keep_files/ukbb_ld_50k_subset.keep" \
          --target "data/ukbb_qc_genotypes/chr_${chrom}" \
          --pheno "data/phenotypes/$trait_type/$pheno_config/$trait.txt" \
          --keep "$keep_file" \
          --pvalue "$p_pval" \
          --snp "$p_snp" \
          --A1 "A1" \
          --stat BETA \
          --thread 7 \
          --binary-target "$binary_target" \
          --print-snp \
          --out "$output_dir/chr_${chrom}"
done

MINUTES=$(echo "scale=2; $SECONDS/60" | bc)

echo "Transforming output..."

source "$HOME/pyenv/bin/activate"
python external/PRSice2/transform_output.py -o "$output_dir" -s "$ss_dir"
python model_fit/combine_fit_files.py -d "data/model_fit/$SLURM_JOB_NAME"

echo "Job finished with exit code $? at: `date`"
echo "Duration (minutes): $MINUTES"
