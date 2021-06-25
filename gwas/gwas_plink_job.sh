#!/bin/bash
#SBATCH --account=def-sgravel
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=8GB
#SBATCH --time=01:00:00
#SBATCH --output=./log/gwas/%x/%j.out
#SBATCH --mail-user=shadi.zabad@mail.mcgill.ca
#SBATCH --mail-type=FAIL

module load plink

chr=${1:-22}  # Chromosome
pheno_file=$2  # The input directory where the phenotype files are stored
standardize=${3:-1}  # Whether to standardize the genotype/phenotype before performing regression (default: TRUE)

# Check that the input directory has been specified
if test -z "$pheno_file"; then
  echo "Error: input directory is not set!"
  exit
fi

config_dir=$(dirname "$pheno_file")
config_name=$(basename "$config_dir")  # The name of the simulation configuration
pheno_id=$(basename "$pheno_file" .txt)  # Extract the phenotype ID

cd /home/szabad/projects/def-sgravel/szabad/viprs-paper || exit

mkdir -p "data/gwas/$config_name/$pheno_id"  # Create the output directory

if [ "${standardize}" == 1 ]; then
  plink2 --bfile "data/ukbb_qc_genotypes/chr_$chr" \
        --linear hide-covar \
        --covar-variance-standardize \
        --keep data/keep_files/ukbb_train_subset.keep \
        --allow-no-sex \
        --pheno "$pheno_file"  \
        --out "data/gwas/$config_name/$pheno_id/chr_$chr"
else
  plink2 --bfile "data/ukbb_qc_genotypes/chr_$chr" \
        --linear hide-covar \
        --keep data/keep_files/ukbb_train_subset.keep \
        --allow-no-sex \
        --pheno "$pheno_file"  \
        --out "data/gwas/$config_name/$pheno_id/chr_$chr"
fi

echo "Job finished with exit code $? at: `date`"
