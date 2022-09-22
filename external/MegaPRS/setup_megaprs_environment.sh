#!/bin/bash
# Download MegaPRS software (MegaPRS v5.2):

echo "Setting up the environment for MegaPRS..."

wget https://dougspeed.com/wp-content/uploads/ldak5.2.linux_.zip -P external/MegaPRS/ || exit

# Unzip and remove the zip file:
unzip external/MegaPRS/ldak5.2.linux_.zip -d external/MegaPRS/
rm external/MegaPRS/ldak5.2.linux_.zip

# Download the pre-computed LD matrices:

# NOTE: No longer using the QuickPRS files.
# wget https://genetics.ghpc.au.dk/doug/gbr.hapmap.tar.gz -P external/MegaPRS/ || exit
# tar -xzvf external/MegaPRS/gbr.hapmap.tar.gz -C external/MegaPRS/gbr.hapmap/
# rm external/MegaPRS/gbr.hapmap.tar.gz

# Get the detailed SNP information for the HapMap3 subset:
#wget https://genetics.ghpc.au.dk/doug/hapmap.allpops.snp.details.gz -P external/MegaPRS/ || exit
#gunzip external/MegaPRS/hapmap.allpops.snp.details.gz

# Compute LD matrices and tagging files using the GCTA model:
mkdir -p external/MegaPRS/ukb_ld/
rm external/MegaPRS/ukb_ld/*_list.txt

for chrom in $(seq 1 22)
do

  # Compute the tagging file for the GCTA model:
  external/MegaPRS/ldak5.2.linux --calc-tagging "external/MegaPRS/ukb_ld/chr_$chrom" \
                                 --bfile "data/ukbb_qc_genotypes/chr_${chrom}" \
                                 --keep "data/keep_files/ukbb_ld_10k_subset.keep" \
                                 --ignore-weights YES \
                                 --power -1 \
                                 --window-cm 1 \
                                 --save-matrix YES \
                                 --chr "$chrom" \
                                 --max-threads 7

  # Compute the SNP-by-SNP correlation matrix:
  external/MegaPRS/ldak5.2.linux --calc-cors "external/MegaPRS/ukb_ld/chr_$chrom" \
                                 --bfile "data/ukbb_qc_genotypes/chr_${chrom}" \
                                 --keep "data/keep_files/ukbb_ld_10k_subset.keep" \
                                 --window-cm 3 \
                                 --chr "$chrom" \
                                 --max-threads 7

  echo "external/MegaPRS/ukb_ld/chr_$chrom.tagging" >> external/MegaPRS/ukb_ld/tagging_list.txt
  echo "external/MegaPRS/ukb_ld/chr_$chrom.matrix" >> external/MegaPRS/ukb_ld/matrix_list.txt
done

# Join the tagging files:
external/MegaPRS/ldak5.2.linux --join-tagging "external/MegaPRS/ukb_ld/combined" \
                               --taglist "external/MegaPRS/ukb_ld/tagging_list.txt" \
                               --matlist "external/MegaPRS/ukb_ld/matrix_list.txt"

# Remove the per-chromosome files:
rm external/MegaPRS/ukb_ld/chr_*.tagging
rm external/MegaPRS/ukb_ld/chr_*.matrix
rm external/MegaPRS/ukb_ld/*_list.txt

# Transform the summary statistics:
source external/MegaPRS/transform_sumstats_job.sh
