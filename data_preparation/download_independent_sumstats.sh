#!/bin/bash

# Create directories for independent sumstats:
mkdir -p ./data/gwas/binary/independent
mkdir -p ./data/gwas/quantitative/independent

# ----------------------------------
# HEIGHT

wget https://storage.googleapis.com/broad-alkesgroup-public/LDSCORE/all_sumstats/PASS_Height1.sumstats \
    -O ./data/gwas/quantitative/independent/PASS_HEIGHT.sumstats
wget https://storage.googleapis.com/broad-alkesgroup-public/LDSCORE/all_sumstats/UKB_460K.body_HEIGHTz.sumstats \
    -O ./data/gwas/quantitative/independent/UKB_HEIGHT.sumstats

# ----------------------------------
# BMI

wget https://storage.googleapis.com/broad-alkesgroup-public/LDSCORE/all_sumstats/PASS_BMI1.sumstats \
    -O ./data/gwas/quantitative/independent/PASS_BMI.sumstats

wget https://storage.googleapis.com/broad-alkesgroup-public/LDSCORE/all_sumstats/UKB_460K.body_BMIz.sumstats \
    -O ./data/gwas/quantitative/independent/UKB_BMI.sumstats

# ----------------------------------
# HDL

wget https://storage.googleapis.com/broad-alkesgroup-public/LDSCORE/all_sumstats/PASS_HDL.sumstats \
    -O ./data/gwas/quantitative/independent/PASS_HDL.sumstats

wget https://storage.googleapis.com/broad-alkesgroup-public/LDSCORE/all_sumstats/UKB_460K.biochemistry_HDLcholesterol.sumstats \
    -O ./data/gwas/quantitative/independent/UKB_HDL.sumstats

# ----------------------------------
# LDL

wget https://storage.googleapis.com/broad-alkesgroup-public/LDSCORE/all_sumstats/PASS_LDL.sumstats \
    -O ./data/gwas/quantitative/independent/PASS_LDL.sumstats

wget https://storage.googleapis.com/broad-alkesgroup-public/LDSCORE/all_sumstats/UKB_460K.biochemistry_LDLdirect.sumstats \
    -O ./data/gwas/quantitative/independent/UKB_LDL.sumstats

# ----------------------------------
# BW

wget https://storage.googleapis.com/broad-alkesgroup-public/LDSCORE/all_sumstats/PASS_FetalBirthWeight_Warrington2019.sumstats \
    -O ./data/gwas/quantitative/independent/PASS_BW.sumstats

# ----------------------------------
# T2D

wget https://storage.googleapis.com/broad-alkesgroup-public/LDSCORE/all_sumstats/PASS_Type_2_Diabetes.sumstats \
    -O ./data/gwas/binary/independent/PASS_T2D.sumstats

wget https://storage.googleapis.com/broad-alkesgroup-public/LDSCORE/all_sumstats/UKB_460K.disease_T2D.sumstats \
    -O ./data/gwas/binary/independent/UKB_T2D.sumstats

# ----------------------------------
# T1D

wget https://storage.googleapis.com/broad-alkesgroup-public/LDSCORE/all_sumstats/PASS_Type_1_Diabetes.sumstats \
    -O ./data/gwas/binary/independent/PASS_T1D.sumstats

# ----------------------------------
# RA

wget https://storage.googleapis.com/broad-alkesgroup-public/LDSCORE/all_sumstats/PASS_Rheumatoid_Arthritis.sumstats \
    -O ./data/gwas/binary/independent/PASS_RA.sumstats

# ----------------------------------
# ASTHMA

wget https://storage.googleapis.com/broad-alkesgroup-public/LDSCORE/all_sumstats/UKB_460K.disease_ASTHMA_DIAGNOSED.sumstats \
    -O ./data/gwas/binary/independent/PASS_ASTHMA.sumstats