#!/bin/bash
#SBATCH --account=def-sgravel
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=1GB
#SBATCH --time=01:00:00
#SBATCH --mail-user=shadi.zabad@mail.mcgill.ca
#SBATCH --mail-type=ALL

module load plink

cd /home/szabad/projects/def-sgravel/szabad/viprs-paper || exit

for pheno in {1..100}
do
  mkdir -p "data/gwas/{$1}/{$pheno}"
  for chr in {1..22}
  do
    plink2 --bfile "data/ukbb_qc_genotypes/chr_{$chr}" \
          --linear hide-covar \
          --covar data/covariates/covar_file.txt \
          --keep data/keep_files/ukbb_train_subset.keep \
          --allow-no-sex \
          --pheno "data/simulated_phenotypes/{$1}/{$pheno}.txt"  \
          --out "data/gwas/{$1}/{$pheno}/{$chr}"  2>&1 | tee "data/gwas/{$1}/{$pheno}/{$chr}.log"
  done
done
