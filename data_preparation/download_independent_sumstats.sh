#!/bin/bash

# ----------------------------------
# HEIGHT

mkdir -p ./data/gwas/quantitative/independent/PASS_HEIGHT
mkdir -p ./data/gwas/quantitative/independent/UKB_HEIGHT
mkdir -p ./data/gwas/quantitative/independent/Yengo_HEIGHT
mkdir -p ./data/gwas/quantitative/independent/Wood_HEIGHT

wget https://storage.googleapis.com/broad-alkesgroup-public/LDSCORE/all_sumstats/PASS_Height1.sumstats \
    -O ./data/gwas/quantitative/independent/PASS_HEIGHT/combined.sumstats
wget https://storage.googleapis.com/broad-alkesgroup-public/LDSCORE/all_sumstats/UKB_460K.body_HEIGHTz.sumstats \
    -O ./data/gwas/quantitative/independent/UKB_HEIGHT/combined.sumstats
wget https://portals.broadinstitute.org/collaboration/giant/images/6/63/Meta-analysis_Wood_et_al%2BUKBiobank_2018.txt.gz \
    -O ./data/gwas/quantitative/independent/Yengo_HEIGHT/combined.sumstats.gz
wget https://portals.broadinstitute.org/collaboration/giant/images/0/01/GIANT_HEIGHT_Wood_et_al_2014_publicrelease_HapMapCeuFreq.txt.gz \
    -O ./data/gwas/quantitative/independent/Wood_HEIGHT/combined.sumstats.gz

gunzip ./data/gwas/quantitative/independent/Yengo_HEIGHT/combined.sumstats.gz
gunzip ./data/gwas/quantitative/independent/Wood_HEIGHT/combined.sumstats.gz

# ----------------------------------
# BMI

mkdir -p ./data/gwas/quantitative/independent/PASS_BMI
mkdir -p ./data/gwas/quantitative/independent/UKB_BMI
mkdir -p ./data/gwas/quantitative/independent/Yengo_BMI
mkdir -p ./data/gwas/quantitative/independent/Locke_BMI

wget https://storage.googleapis.com/broad-alkesgroup-public/LDSCORE/all_sumstats/PASS_BMI1.sumstats \
    -O ./data/gwas/quantitative/independent/PASS_BMI/combined.sumstats
wget https://storage.googleapis.com/broad-alkesgroup-public/LDSCORE/all_sumstats/UKB_460K.body_BMIz.sumstats \
    -O ./data/gwas/quantitative/independent/UKB_BMI/combined.sumstats
wget https://portals.broadinstitute.org/collaboration/giant/images/c/c8/Meta-analysis_Locke_et_al%2BUKBiobank_2018_UPDATED.txt.gz \
    -O ./data/gwas/quantitative/independent/Yengo_BMI/combined.sumstats.gz
wget https://portals.broadinstitute.org/collaboration/giant/images/1/15/SNP_gwas_mc_merge_nogc.tbl.uniq.gz \
    -O ./data/gwas/quantitative/independent/Locke_BMI/combined.sumstats.gz

gunzip ./data/gwas/quantitative/independent/Yengo_BMI/combined.sumstats.gz
gunzip ./data/gwas/quantitative/independent/Locke_BMI/combined.sumstats.gz

# ----------------------------------
# HDL

mkdir -p ./data/gwas/quantitative/independent/PASS_HDL
mkdir -p ./data/gwas/quantitative/independent/UKB_HDL

wget https://storage.googleapis.com/broad-alkesgroup-public/LDSCORE/all_sumstats/PASS_HDL.sumstats \
    -O ./data/gwas/quantitative/independent/PASS_HDL/combined.sumstats

wget https://storage.googleapis.com/broad-alkesgroup-public/LDSCORE/all_sumstats/UKB_460K.biochemistry_HDLcholesterol.sumstats \
    -O ./data/gwas/quantitative/independent/UKB_HDL/combined.sumstats

# ----------------------------------
# LDL

mkdir -p ./data/gwas/quantitative/independent/PASS_LDL
mkdir -p ./data/gwas/quantitative/independent/UKB_LDL

wget https://storage.googleapis.com/broad-alkesgroup-public/LDSCORE/all_sumstats/PASS_LDL.sumstats \
    -O ./data/gwas/quantitative/independent/PASS_LDL/combined.sumstats
wget https://storage.googleapis.com/broad-alkesgroup-public/LDSCORE/all_sumstats/UKB_460K.biochemistry_LDLdirect.sumstats \
    -O ./data/gwas/quantitative/independent/UKB_LDL/combined.sumstats

# ----------------------------------
# BW

mkdir -p ./data/gwas/quantitative/independent/PASS_BW

wget https://storage.googleapis.com/broad-alkesgroup-public/LDSCORE/all_sumstats/PASS_FetalBirthWeight_Warrington2019.sumstats \
    -O ./data/gwas/quantitative/independent/PASS_BW/combined.sumstats

# ----------------------------------
# T2D

mkdir -p ./data/gwas/binary/independent/PASS_T2D
mkdir -p ./data/gwas/binary/independent/UKB_T2D

wget https://storage.googleapis.com/broad-alkesgroup-public/LDSCORE/all_sumstats/PASS_Type_2_Diabetes.sumstats \
    -O ./data/gwas/binary/independent/PASS_T2D/combined.sumstats
wget https://storage.googleapis.com/broad-alkesgroup-public/LDSCORE/all_sumstats/UKB_460K.disease_T2D.sumstats \
    -O ./data/gwas/binary/independent/UKB_T2D/combined.sumstats

# ----------------------------------
# T1D

mkdir -p ./data/gwas/binary/independent/PASS_T1D

wget https://storage.googleapis.com/broad-alkesgroup-public/LDSCORE/all_sumstats/PASS_Type_1_Diabetes.sumstats \
    -O ./data/gwas/binary/independent/PASS_T1D/combined.sumstats

# ----------------------------------
# RA

mkdir -p ./data/gwas/binary/independent/PASS_RA

wget https://storage.googleapis.com/broad-alkesgroup-public/LDSCORE/all_sumstats/PASS_Rheumatoid_Arthritis.sumstats \
    -O ./data/gwas/binary/independent/PASS_RA/combined.sumstats

# ----------------------------------
# ASTHMA

mkdir -p ./data/gwas/binary/independent/PASS_ASTHMA

wget https://storage.googleapis.com/broad-alkesgroup-public/LDSCORE/all_sumstats/UKB_460K.disease_ASTHMA_DIAGNOSED.sumstats \
    -O ./data/gwas/binary/independent/PASS_ASTHMA/combined.sumstats