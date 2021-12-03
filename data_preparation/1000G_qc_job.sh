#!/bin/bash
#SBATCH --account=def-sgravel
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=8GB
#SBATCH --time=00:10:00
#SBATCH --output=./log/data_preparation/%x/%j.out
#SBATCH --mail-user=shadi.zabad@mail.mcgill.ca
#SBATCH --mail-type=FAIL

module load plink

cd /home/szabad/projects/def-sgravel/szabad/viprs-paper || exit

CHR=${1:-22}  # Chromosome number (default 22)
snp_set=${2:-"hm3"} # The SNP set to use

if [ $snp_set == "hm3" ]; then
  snp_keep="data/keep_files/ukbb_qc_variants_hm3.keep"
  output_dir="data/1000G_qc_genotypes"
else
  snp_keep="data/keep_files/ukbb_qc_variants.keep"
  output_dir="/scratch/szabad/data/1000G_qc_genotypes_all"
fi

mkdir -p "$output_dir"

plink2 --bfile "$HOME/projects/def-sgravel/data/genotypes/1000G_EUR_Phase3_plink/1000G.EUR.QC.$CHR" \
      --make-bed \
      --allow-no-sex \
      --extract "$snp_keep" \
      --hwe 1e-10 \
      --mind 0.05 \
      --geno 0.05 \
      --mac 5 \
      --maf 0.0001 \
      --max-maf 0.9999 \
      --snps-only \
      --max-alleles 2 \
      --out "$output_dir/chr_${CHR}"

module load nixpkgs/16.09
module load plink/1.9b_4.1-x86_64

# Update the SNP cM position using the HapMap3 genetic map:
plink --bfile "$output_dir/chr_${CHR}" \
      --cm-map "$HOME/projects/def-sgravel/data/genetic_maps/1000GP_Phase3/genetic_map_chr@_combined_b37.txt" \
      --make-bed \
      --mac 5 \
      --maf 0.0001 \
      --max-maf 0.9999 \
      --out "$output_dir/chr_${CHR}"

rm -r "$output_dir"/*~

echo "Job finished with exit code $? at: `date`"
