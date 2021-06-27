#!/bin/bash
#SBATCH --account=def-sgravel
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=4GB
#SBATCH --time=00:20:00
#SBATCH --output=./log/model_fit/%x/%j.out
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
ss_file=$1 # Summary statistics file
chrom=$2   # Chromosome number

ss_dir=$(dirname $ss_file)
trait=$(basename "$ss_dir")
config_dir=$(dirname $ss_dir)
config=$(basename "$config_dir")

mkdir -p "data/model_fit/external/PRSice2/$config/$trait/"

SECONDS=0

Rscript "$PRSiceHome/PRSice.R" \
        --dir "$R_LIBS" \
        --prsice "$PRSiceHome/PRSice_linux" \
        --base "$ss_file" \
        --ld "data/ukbb_qc_genotypes/chr_$chrom" \
        --ld-keep "data/keep_files/ukbb_ld_50k_subset.keep" \
        --target "data/ukbb_qc_genotypes/chr_$chrom" \
        --pheno "data/phenotypes/$config/$trait.txt" \
        --keep "data/keep_files/ukbb_valid_subset.keep" \
        --pvalue PVAL \
        --stat BETA \
        --binary-target F \
        --print-snp \
        --out "data/model_fit/external/PRSice2/$config/$trait/chr_$chrom"

MINUTES=$(echo "scale=2; $SECONDS/60" | bc)

echo "Transforming output..."

source "$HOME/pyenv/bin/activate"
python external/PRSice2/transform_output.py "data/model_fit/external/PRSice2/$config/$trait/chr_$chrom" "$ss_file"

echo "Job finished with exit code $? at: `date`"
echo "Duration (minutes): $MINUTES"
