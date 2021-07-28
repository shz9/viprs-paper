#!/bin/bash
#SBATCH --account=def-sgravel
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=4GB
#SBATCH --time=00:30:00
#SBATCH --output=./log/model_fit/%x.out
#SBATCH --mail-user=shadi.zabad@mail.mcgill.ca
#SBATCH --mail-type=FAIL

echo "Job started at: `date`"
echo "Performing model fit..."
echo "Dataset: $1"
echo "Model: PRSice2"

module load gcc/9.3.0 r/4.0.2
export R_LIBS=$HOME/projects/def-sgravel/R_environments/R_4.0.2/prsice

PRSiceHome=$HOME/projects/def-sgravel/bin/PRSice_v2.3.3

# Inputs:
ss_dir=$(readlink -e "$1")  # Summary statistics directory
keep_file=$2   # Individual keep file for samples in the validation set
sumstats_type=${3:-"plink"}

trait=$(basename "$ss_dir")
config=$(basename "$(dirname "$ss_dir")")

output_dir="data/model_fit/external/PRSice2/$config/$trait/"

mkdir -p "$output_dir"

if [ "$sumstats_type" == "plink" ]; then
  p_pval="P"
  p_chrom="#CHROM"
  p_snp="ID"
else
  p_pval="PVAL"
  p_chrom="CHR"
  p_snp="SNP"
fi

SECONDS=0

for chrom in $(seq 1 22)
do
  Rscript "$PRSiceHome/PRSice.R" \
          --dir "$R_LIBS" \
          --prsice "$PRSiceHome/PRSice_linux" \
          --base "$ss_dir/chr_${chrom}.PHENO1.glm.linear" \
          --ld "data/ukbb_qc_genotypes/chr_${chrom}" \
          --ld-keep "data/keep_files/ukbb_ld_50k_subset.keep" \
          --target "data/ukbb_qc_genotypes/chr_${chrom}" \
          --pheno "data/phenotypes/$config/$trait.txt" \
          --keep "$keep_file" \
          --pvalue "$p_pval" \
          --chr "$p_chrom" \
          --snp "$p_snp" \
          --stat BETA \
          --binary-target F \
          --print-snp \
          --out "$output_dir/chr_${chrom}"
done

MINUTES=$(echo "scale=2; $SECONDS/60" | bc)

echo "Transforming output..."

source "$HOME/pyenv/bin/activate"
python external/PRSice2/transform_output.py -o "$output_dir" -s "$ss_dir"

echo "Job finished with exit code $? at: `date`"
echo "Duration (minutes): $MINUTES"
