#!/bin/bash
#SBATCH --account=def-sgravel
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=8GB
#SBATCH --time=02:00:00
#SBATCH --output=./log/data_preparation/%x/%j.out
#SBATCH --mail-user=shadi.zabad@mail.mcgill.ca
#SBATCH --mail-type=FAIL

echo "Job started at: `date`"
echo "Job ID: $SLURM_JOBID"

. global_config.sh

module load plink

cd "$VIPRS_PATH" || exit

CHR=${1:-22}  # Chromosome number (default 22)
snp_set=${2:-"hm3"} # The SNP set to use

if [ $snp_set == "hm3" ]; then
  snp_keep="data/keep_files/ukbb_qc_variants_hm3.keep"
  output_dir="data/ukbb_qc_genotypes"
else
  snp_keep="data/keep_files/ukbb_qc_variants.keep"
  output_dir="/scratch/szabad/data/ukbb_qc_genotypes_all"
fi

mkdir -p "$output_dir"

plink2 --bgen "$UKBB_GENOTYPE_DIR/ukb_imp_chr${CHR}_v3.bgen" ref-first \
      --sample "$UKBB_GENOTYPE_DIR/ukb6728_imp_chr${CHR}_v3_s487395.sample" \
      --make-bed \
      --allow-no-sex \
      --keep data/keep_files/ukbb_qc_individuals.keep \
      --extract "$snp_keep" \
      --hwe "$HWE_CUTOFF" \
      --mind "$MIND" \
      --geno "$GENO" \
      --mac "$MIN_MAC" \
      --maf "$MIN_MAF" \
      --max-maf "$MAX_MAF" \
      --snps-only \
      --max-alleles 2 \
      --hard-call-threshold "$HARDCALL_THRES" \
      --out "$output_dir/chr_${CHR}"

module load nixpkgs/16.09
module load plink/1.9b_4.1-x86_64
# Update the SNP cM position using the HapMap3 genetic map:
# NOTE: We filter on mac/maf again because plink2 sometimes doesn't filter SNPs
# properly in the first step (to be checked later).
plink --bfile "$output_dir/chr_${CHR}" \
      --cm-map "$GENETIC_MAP_DIR/genetic_map_chr@_combined_b37.txt" \
      --make-bed \
      --mac "$MIN_MAC" \
      --maf "$MIN_MAF" \
      --out "$output_dir/chr_${CHR}"

rm -r "$output_dir"/*~

echo "Job finished with exit code $? at: `date`"
