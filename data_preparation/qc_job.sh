#!/bin/bash
#SBATCH --account=def-sgravel
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=2GB
#SBATCH --time=1:00:00
#SBATCH --output=./log/data_preparation/qc/%j.out
#SBATCH --mail-user=shadi.zabad@mail.mcgill.ca
#SBATCH --mail-type=FAIL

module load plink

cd /home/szabad/projects/def-sgravel/szabad/viprs-paper || exit
mkdir -p "data/ukbb_qc_genotypes/"

CHR=${1:-22}  # Chromosome number (default 22)

plink2 --bgen "/lustre03/project/6004777/projects/uk_biobank/imputed_data/full_UKBB/v3_bgen12/ukb_imp_chr${CHR}_v3.bgen" \
      --sample "/lustre03/project/6004777/projects/uk_biobank/imputed_data/full_UKBB/v3_bgen12/ukb6728_imp_chr${CHR}_v3_s487395.sample" \
      --make-bed \
      --allow-no-sex \
      --keep data/keep_files/ukbb_qc_individuals.keep \
      --extract data/keep_files/ukbb_qc_variants_hm3.keep \
      --hwe 1e-10 \
      --mind 0.05 \
      --geno 0.05 \
      --maf 0.001 \
      --snps-only \
      --max-alleles 2 \
      --hard-call-threshold 0.1 \
      --out "data/ukbb_qc_genotypes/chr_${CHR}"

module load nixpkgs/16.09
module load plink/1.9b_4.1-x86_64
# Update the SNP cM position using the HapMap3 genetic map:
plink --bfile "data/ukbb_qc_genotypes/chr_${CHR}" \
      --cm-map "../data/genetic_map/1000GP_Phase3/genetic_map_chr@_combined_b37.txt" \
      --make-bed \
      --out "data/ukbb_qc_genotypes/chr_${CHR}"

rm "data/ukbb_qc_genotypes/*~"

echo "Job finished with exit code $? at: `date`"
