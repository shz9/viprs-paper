#!/bin/bash
#SBATCH --account=def-sgravel
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=8GB
#SBATCH --time=01:20:00
#SBATCH --output=./log/data_preparation/ukbb_qc/%j.out
#SBATCH --mail-user=shadi.zabad@mail.mcgill.ca
#SBATCH --mail-type=FAIL

echo "Job started at: `date`"
echo "Job ID: $SLURM_JOBID"

module load plink

cd /home/szabad/projects/def-sgravel/szabad/viprs-paper || exit

CHR=${1:-22}  # Chromosome number (default 22)
snp_set=${2:-"hm3"} # The SNP set to use

if [ $snp_set == "hm3" ]; then
  snp_keep="data/keep_files/ukbb_qc_variants_hm3.keep"
  output_dir="data/ukbb_qc_genotypes"
else
  snp_keep="data/keep_files/ukbb_qc_variants.keep"
  output_dir="data/ukbb_qc_genotypes_all"
fi

mkdir -p "$output_dir"

plink2 --bgen "/lustre03/project/6004777/projects/uk_biobank/imputed_data/full_UKBB/v3_bgen12/ukb_imp_chr${CHR}_v3.bgen" \
      --sample "/lustre03/project/6004777/projects/uk_biobank/imputed_data/full_UKBB/v3_bgen12/ukb6728_imp_chr${CHR}_v3_s487395.sample" \
      --make-bed \
      --allow-no-sex \
      --keep data/keep_files/ukbb_qc_individuals.keep \
      --extract "$snp_keep" \
      --hwe 1e-10 \
      --mind 0.05 \
      --geno 0.05 \
      --mac 5 \
      --snps-only \
      --max-alleles 2 \
      --hard-call-threshold 0.1 \
      --out "$output_dir/chr_${CHR}"

module load nixpkgs/16.09
module load plink/1.9b_4.1-x86_64
# Update the SNP cM position using the HapMap3 genetic map:
plink --bfile "$output_dir/chr_${CHR}" \
      --cm-map "$HOME/projects/def-sgravel/data/genetic_maps/1000GP_Phase3/genetic_map_chr@_combined_b37.txt" \
      --make-bed \
      --out "$output_dir/chr_${CHR}"

rm -r "$output_dir"/*~

echo "Job finished with exit code $? at: `date`"
