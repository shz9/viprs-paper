#!/bin/bash

mkdir -p ./data/external_gwas/quantitative/
mkdir -p ./data/external_gwas/binary/

# ----------------------------------
# HEIGHT

wget https://storage.googleapis.com/broad-alkesgroup-public/LDSCORE/all_sumstats/PASS_Height1.sumstats \
    -O ./data/external_gwas/quantitative/PASS_HEIGHT.sumstats
#wget https://storage.googleapis.com/broad-alkesgroup-public/LDSCORE/all_sumstats/UKB_460K.body_HEIGHTz.sumstats \
#    -O ./data/external_gwas/quantitative/UKB_HEIGHT.sumstats
#wget https://portals.broadinstitute.org/collaboration/giant/images/6/63/Meta-analysis_Wood_et_al%2BUKBiobank_2018.txt.gz \
#    -O ./data/external_gwas/quantitative/Yengo_HEIGHT.sumstats.gz
#wget https://portals.broadinstitute.org/collaboration/giant/images/0/01/GIANT_HEIGHT_Wood_et_al_2014_publicrelease_HapMapCeuFreq.txt.gz \
#    -O ./data/external_gwas/quantitative/Wood_HEIGHT.sumstats.gz

#gunzip ./data/external_gwas/quantitative/Yengo_HEIGHT.sumstats.gz
#gunzip ./data/external_gwas/quantitative/Wood_HEIGHT.sumstats.gz

# ----------------------------------
# BMI

wget https://storage.googleapis.com/broad-alkesgroup-public/LDSCORE/all_sumstats/PASS_BMI1.sumstats \
    -O ./data/external_gwas/quantitative/PASS_BMI.sumstats
#wget https://storage.googleapis.com/broad-alkesgroup-public/LDSCORE/all_sumstats/UKB_460K.body_BMIz.sumstats \
#    -O ./data/external_gwas/quantitative/UKB_BMI.sumstats
#wget https://portals.broadinstitute.org/collaboration/giant/images/c/c8/Meta-analysis_Locke_et_al%2BUKBiobank_2018_UPDATED.txt.gz \
#    -O ./data/external_gwas/quantitative/Yengo_BMI.sumstats.gz
#wget https://portals.broadinstitute.org/collaboration/giant/images/1/15/SNP_gwas_mc_merge_nogc.tbl.uniq.gz \
#    -O ./data/external_gwas/quantitative/Locke_BMI.sumstats.gz

#gunzip ./data/external_gwas/quantitative/Yengo_BMI.sumstats.gz
#gunzip ./data/external_gwas/quantitative/Locke_BMI.sumstats.gz

# ----------------------------------
# HDL


wget https://storage.googleapis.com/broad-alkesgroup-public/LDSCORE/all_sumstats/PASS_HDL.sumstats \
    -O ./data/external_gwas/quantitative/PASS_HDL.sumstats

# ----------------------------------
# LDL

wget https://storage.googleapis.com/broad-alkesgroup-public/LDSCORE/all_sumstats/PASS_LDL.sumstats \
    -O ./data/external_gwas/quantitative/PASS_LDL.sumstats

# ----------------------------------
# BW

#wget https://storage.googleapis.com/broad-alkesgroup-public/LDSCORE/all_sumstats/PASS_FetalBirthWeight_Warrington2019.sumstats \
#    -O ./data/external_gwas/quantitative/PASS_BW.sumstats

# ----------------------------------
# T2D

wget https://storage.googleapis.com/broad-alkesgroup-public/LDSCORE/all_sumstats/PASS_Type_2_Diabetes.sumstats \
    -O ./data/external_gwas/binary/PASS_T2D.sumstats
#wget https://storage.googleapis.com/broad-alkesgroup-public/LDSCORE/all_sumstats/UKB_460K.disease_T2D.sumstats \
#    -O ./data/external_gwas/binary/UKB_T2D.sumstats

# ----------------------------------
# RA

wget https://storage.googleapis.com/broad-alkesgroup-public/LDSCORE/all_sumstats/PASS_Rheumatoid_Arthritis.sumstats \
    -O ./data/external_gwas/binary/PASS_RA.sumstats

# ----------------------------------
# ASTHMA

#wget https://storage.googleapis.com/broad-alkesgroup-public/LDSCORE/all_sumstats/UKB_460K.disease_ASTHMA_DIAGNOSED.sumstats \
#    -O ./data/external_gwas/binary/PASS_ASTHMA.sumstats


# ----------------------------------

# Transform the summary statistics files to match the format required by the rest of the pipeline:

source "$HOME/pyenv/bin/activate"
python data_preparation/transform_external_sumstats.py
python data_preparation/transform_external_sumstats.py --genotype-dir data_all/ukbb_qc_genotypes
