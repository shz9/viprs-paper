#!/bin/bash
#SBATCH --account=def-sgravel
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=1GB
#SBATCH --time=2:00:00
#SBATCH --mail-user=shadi.zabad@mail.mcgill.ca
#SBATCH --mail-type=ALL

module load plink

cd /home/szabad/projects/def-sgravel/szabad/viprs-paper || exit
mkdir -p "data/ukbb_qc_genotypes/"

plink2 --pfile "/lustre03/project/6004777/projects/uk_biobank/imputed_data/full_UKBB/v3_plink2/ukb_imp_chr$1_v3" \
      --make-bed \
      --allow-no-sex \
      --keep data/keep_files/ukbb_qc_individuals.keep \
      --extract data/keep_files/ukbb_qc_variants_hm3.keep \
      --cm-map "../data/genetic_map/1000GP_Phase3/genetic_map_chr$1_combined_b37.txt" \
      --hwe 1e-10 \
      --geno 0.05 \
      --maf 0.001 \
      --snps-only \
      --max-alleles 2 \
      --out "data/ukbb_qc_genotypes/chr_$1"
