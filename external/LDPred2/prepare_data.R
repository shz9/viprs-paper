# This script takes the combined .bed file in PLINK format
# and converts it to bigSNP object for the purposes of fitting
# LDPred2 to GWAS Summary statistics
library(bigsnpr)

snp_readBed2("data/ukbb_qc_genotypes/combined.bed",
             backingfile="data/ukbb_qc_genotypes/UKBB_imp_hm3")
