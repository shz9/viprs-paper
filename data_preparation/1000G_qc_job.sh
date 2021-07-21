#!/bin/bash
#SBATCH --account=def-sgravel
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=8GB
#SBATCH --time=00:10:00
#SBATCH --output=./log/data_preparation/1000G_qc/%j.out
#SBATCH --mail-user=shadi.zabad@mail.mcgill.ca
#SBATCH --mail-type=FAIL

module load plink

cd /home/szabad/projects/def-sgravel/szabad/viprs-paper || exit
mkdir -p "data/1000G_qc_genotypes/"

CHR=${1:-22}  # Chromosome number (default 22)

plink2 --bfile "$HOME/projects/def-sgravel/data/genotypes/1000G_EUR_Phase3_plink/1000G.EUR.QC.$CHR" \
      --make-bed \
      --allow-no-sex \
      --extract data/keep_files/ukbb_qc_variants_hm3.keep \
      --hwe 1e-10 \
      --mind 0.05 \
      --geno 0.05 \
      --maf 0.001 \
      --mac 5 \
      --snps-only \
      --max-alleles 2 \
      --out "data/1000G_qc_genotypes/chr_${CHR}"

module load nixpkgs/16.09
module load plink/1.9b_4.1-x86_64

# Update the SNP cM position using the HapMap3 genetic map:
plink --bfile "data/1000G_qc_genotypes/chr_${CHR}" \
      --cm-map "$HOME/projects/def-sgravel/data/genetic_maps/1000GP_Phase3/genetic_map_chr@_combined_b37.txt" \
      --make-bed \
      --out "data/1000G_qc_genotypes/chr_${CHR}"

rm -r data/1000G_qc_genotypes/*~

echo "Job finished with exit code $? at: `date`"
