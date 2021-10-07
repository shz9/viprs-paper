#!/bin/bash
#SBATCH --account=def-sgravel
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=2GB
#SBATCH --time=01:00:00
#SBATCH --output=./log/gwas/%x.out
#SBATCH --mail-user=shadi.zabad@mail.mcgill.ca
#SBATCH --mail-type=FAIL

echo "Job started at: `date`"
echo "Job ID: $SLURM_JOBID"

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
reg_type=$(basename $(dirname "$config_dir")) # The regression type (logistic/linear)
config_name=$(basename "$config_dir")  # The name of the simulation configuration
pheno_id=$(basename "$pheno_file" .txt)  # Extract the phenotype ID

# Parse optional parameters:
opt_params=()

if [ "${reg_type}" == "binary" ]; then
  reg_type="logistic"
  opt_params+=(--1)
else
  reg_type="linear"
fi

if [ "${standardize}" == 1 ]; then
  opt_params+=(--variance-standardize)
fi

cd /home/szabad/projects/def-sgravel/szabad/viprs-paper || exit

mkdir -p "$output_dir"  # Create the output directory

for chr in $(seq 1 22)
do
  plink2 --bfile "data/ukbb_qc_genotypes/chr_$chr" \
         --"$reg_type" hide-covar cols=chrom,pos,alt1,ref,a1freq,nobs,beta,se,tz,p \
         --keep "$keep_file" \
         --allow-no-sex \
         --maf 0.01 \
         --mac 5 \
         --pheno "$pheno_file"  \
         --out "$output_dir/chr_$chr" \
         "${opt_params[@]}"
done

echo "Job finished with exit code $? at: `date`"
