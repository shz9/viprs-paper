#!/bin/bash
#SBATCH --account=def-sgravel
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=2GB
#SBATCH --time=01:00:00
#SBATCH --output=./log/gwas/%x.out
#SBATCH --mail-user=shadi.zabad@mail.mcgill.ca
#SBATCH --mail-type=FAIL

module load plink

pheno_file=$1  # The input file path
keep_file=${2:-"data/keep_files/ukbb_train_subset.keep"}
output_dir=$3
standardize=${4:-1}  # Whether to standardize the genotype/phenotype before performing regression (default: TRUE)

# Check that the input directory has been specified
if test -z "$pheno_file"; then
  echo "Error: input directory is not set!"
  exit
fi

config_dir=$(dirname "$pheno_file")
config_name=$(basename "$config_dir")  # The name of the simulation configuration
pheno_id=$(basename "$pheno_file" .txt)  # Extract the phenotype ID

cd /home/szabad/projects/def-sgravel/szabad/viprs-paper || exit

mkdir -p "$output_dir"  # Create the output directory

for chr in $(seq 1 22)
do
  if [ "${standardize}" == 1 ]; then
    plink2 --bfile "data/ukbb_qc_genotypes/chr_$chr" \
          --linear hide-covar \
          --variance-standardize \
          --keep "$keep_file" \
          --allow-no-sex \
          --pheno "$pheno_file"  \
          --out "$output_dir/chr_$chr"
  else
    plink2 --bfile "data/ukbb_qc_genotypes/chr_$chr" \
          --linear hide-covar \
          --keep "$keep_file" \
          --allow-no-sex \
          --pheno "$pheno_file"  \
          --out "$output_dir/chr_$chr"
  fi
done

echo "Job finished with exit code $? at: `date`"
