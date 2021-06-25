#!/bin/bash

gwas_software=${1:-"python"}
setup=${2:-"simulation"}

echo "Submitting jobs for performing GWAS with $gwas_software..."

# For simulation, we only consider chromosome 22
# For real phenotypes, we need all autosomal chromosomes
if [ "$setup" == "simulation" ]; then
  chromosomes=(22)
  input_files=($(ls data/phenotypes/h2_*/*.txt))
else
  chromosomes=($(seq 1 22))
  input_files=($(ls data/phenotypes/real/*.txt))
fi

# Prepare the loggin directory:
rm -rf "./log/gwas/$gwas_software/$setup" || true
mkdir -p "./log/gwas/$gwas_software/$setup"

# Loop over the phenotype files and submit GWAS jobs:
for pheno_file in "${input_files[@]}"
do
  for chr in "${chromosomes[@]}"
  do
    echo "Submitting GWAS job for Chromosome $chr and phenotypes file $pheno_file"
    if [ "$gwas_software" == "plink" ]; then
      sbatch -J "plink/$setup" gwas/gwas_plink_job.sh "$chr" "$pheno_file"
    else
      if [[ $(wc -l <"data/ukbb_qc_genotypes/chr_$chr.bim") -ge 50000 ]]; then
        # Temporary fix for memory errors...
        # If the chromosome has >50k SNPs, assign the compute node more memory than the default 8GB.
        sbatch -J "python/$setup" --mem-per-cpu "14GB" gwas/gwas_python_job.sh "$chr" "$pheno_file"
      else
        sbatch -J "python/$setup" gwas/gwas_python_job.sh "$chr" "$pheno_file"
      fi
    fi
  done
done
