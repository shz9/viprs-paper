#!/bin/bash
#SBATCH --account=def-sgravel
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=4GB
#SBATCH --time=00:10:00
#SBATCH --output=./log/model_fit/%x/%j.out
#SBATCH --mail-user=shadi.zabad@mail.mcgill.ca
#SBATCH --mail-type=FAIL

echo "Job started at: `date`"

module load gcc/9.3.0 r/4.0.2
export R_LIBS=$HOME/projects/def-sgravel/R_environments/R_4.0.2/prsice

PRSiceHome=$HOME/projects/def-sgravel/bin/PRSice_v2.3.3

trait_dir=$(dirname $1)
trait=$(basename "$trait_dir")
config_dir=$(dirname $trait_dir)
config=$(basename "$config_dir")

mkdir -p "data/model_fit/external/PRSice2/$config/$trait/"

SECONDS=0

Rscript "$PRSiceHome/PRSice.R" \
        --dir "$R_LIBS" \
        --prsice "$PRSiceHome/PRSice_linux" \
        --base "$1" \
        --ld "data/ukbb_qc_genotypes/chr_22" \
        --ld-keep "data/keep_files/ukbb_ld_50k_subset.keep" \
        --target "data/ukbb_qc_genotypes/chr_22" \
        --pheno "data/simulated_phenotypes/$config/$trait.txt" \
        --keep "data/keep_files/ukbb_valid_subset.keep" \
        --pvalue PVAL \
        --stat BETA \
        --binary-target F \
        --print-snp \
        --out "data/model_fit/external/PRSice2/$config/$trait/chr_22"

MINUTES=$(echo "scale=2; $SECONDS/60" | bc)

echo "Transforming output..."

source "$HOME/pyenv/bin/activate"
python external/PRSice2/transform_output.py "data/model_fit/external/PRSice2/$config/$trait/chr_22" "$1"

echo "Job finished with exit code $? at: `date`"
echo "Duration (minutes): $MINUTES"
