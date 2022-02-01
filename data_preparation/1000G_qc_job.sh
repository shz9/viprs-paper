#!/bin/bash
#SBATCH --account=def-sgravel
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=8GB
#SBATCH --time=00:10:00
#SBATCH --output=./log/data_preparation/%x/%j.out
#SBATCH --mail-user=shadi.zabad@mail.mcgill.ca
#SBATCH --mail-type=FAIL

# Source the script with the global configurations:
. global_config.sh

module load plink

cd "$VIPRS_PATH" || exit

CHR=${1:-22}  # Chromosome number (default 22)
snp_set=${2:-"hm3"} # The SNP set to use

if [ $snp_set == "hm3" ]; then
  snp_keep="data/keep_files/ukbb_qc_variants_hm3.keep"
  output_dir="data/1000G_qc_genotypes"
else
  snp_keep="data/keep_files/ukbb_qc_variants.keep"
  output_dir="data_all/1000G_qc_genotypes"
fi

mkdir -p "$output_dir"

plink2 --bfile "$TGP_GENOTYPE_DIR/1000G.EUR.QC.$CHR" \
      --make-bed \
      --allow-no-sex \
      --extract "$snp_keep" \
      --hwe "$HWE_CUTOFF" \
      --mind "$MIND" \
      --geno "$GENO" \
      --mac "$MIN_MAC" \
      --maf "$MIN_MAF" \
      --max-maf "$MAX_MAF" \
      --snps-only \
      --max-alleles 2 \
      --out "$output_dir/chr_${CHR}"

# Compute the allele frequency and store in the same directory
# (May be useful in some downstream tasks)
plink2 --bfile "$output_dir/chr_${CHR}" \
       --freq cols=chrom,pos,ref,alt1,alt1freq,nobs \
       --out "$output_dir/chr_${CHR}"


module load nixpkgs/16.09
module load plink/1.9b_4.1-x86_64

# Update the SNP cM position using the HapMap3 genetic map:
plink --bfile "$output_dir/chr_${CHR}" \
      --cm-map "$GENETIC_MAP_DIR/genetic_map_chr@_combined_b37.txt" \
      --make-bed \
      --mac "$MIN_MAC" \
      --maf "$MIN_MAF" \
      --max-maf "$MAX_MAF" \
      --out "$output_dir/chr_${CHR}"

rm -r "$output_dir"/*~

echo "Job finished with exit code $? at: `date`"
