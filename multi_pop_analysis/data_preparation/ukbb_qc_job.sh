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
ind_keep_file=${3-"data/keep_files/ukbb_qc_individuals_minority.keep"}
output_dir=${4-"data/ukbb_qc_genotypes_minority"}
snp_keep="data/keep_files/ukbb_qc_variants_hm3.keep"


mkdir -p "$output_dir"

plink2 --bgen "$UKBB_GENOTYPE_DIR/ukb_imp_chr${CHR}_v3.bgen" ref-first \
      --sample "$UKBB_GENOTYPE_DIR/ukb6728_imp_chr${CHR}_v3_s487395.sample" \
      --make-bed \
      --allow-no-sex \
      --keep "$ind_keep_file" \
      --extract "$snp_keep" \
      --snps-only \
      --max-alleles 2 \
      --hard-call-threshold "$HARDCALL_THRES" \
      --out "$output_dir/chr_${CHR}"

echo "Job finished with exit code $? at: `date`"
