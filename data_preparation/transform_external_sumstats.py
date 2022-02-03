import shutil
import glob
import os.path as osp
from scipy import stats
import numpy as np
import pandas as pd
import argparse
import sys
sys.path.append(osp.dirname(osp.dirname(__file__)))
from utils import makedir

# Transform external summary statistics files to have the same format
# as the output of PLINK2 and split them into multiple chromosomes.
# PLINK2 format used in this analysis pipeline:
# #CHROM	POS	ID	REF	ALT1	A1	A1_FREQ	OBS_CT	BETA	SE	T_STAT	P
#
# For LDSC-style sumstats, we need to add the following columns:
# - A1_FREQ
# - BETA
# - SE
# - P

parser = argparse.ArgumentParser(description='Transform external and publicly available summary statistics')
parser.add_argument('--genotype-dir', dest='genotype_dir', type=str, default='data/ukbb_qc_genotypes')
args = parser.parse_args()

# ----------------------------------------------------------------------------------------------------------------------
# Helper functions


def compute_beta(ss_df):
    """
    Computes the effect size (BETA) from summary statistics,
    following Section 2 in the Supplementary Text of Zhu et al. 2016

    Integration of summary data from GWAS and eQTL studies predicts complex trait gene targets
    Zhu et al. 2016

    :param ss_df:
    """
    z = ss_df.Z.values
    p = ss_df.A1_FREQ.values
    n = ss_df.N.values

    return z / np.sqrt(2. * p * (1. - p) * (n + z ** 2))


def compute_se(ss_df):
    """
    Computes the standard errors from summary statistics,
    following Section 2 in the Supplementary Text of Zhu et al. 2016

    Integration of summary data from GWAS and eQTL studies predicts complex trait gene targets
    Zhu et al. 2016

    :param ss_df:
    """
    z = ss_df.Z.values
    p = ss_df.A1_FREQ.values
    n = ss_df.N.values

    return 1. / np.sqrt(2. * p * (1. - p) * (n + z ** 2))


def transform_ldsc_sumstats(ldsc_file):

    ldsc_df = pd.read_csv(ldsc_file, delim_whitespace=True)
    ldsc_df.drop_duplicates(subset='SNP', keep=False, inplace=True)

    if '/binary/' in ldsc_file:
        trait_type = 'binary'
        extension = ".PHENO1.glm.logistic"
    else:
        trait_type = 'quantitative'
        extension = ".PHENO1.glm.linear"

    trait_name = osp.basename(ldsc_file).replace('.sumstats', '')

    for freq_file in glob.glob(osp.join(args.genotype_dir, "*.afreq")):

        freq_df = pd.read_csv(freq_file, delim_whitespace=True)

        m_df = freq_df.merge(ldsc_df, left_on='ID', right_on='SNP')

        # Correct allele frequency:
        a1_mismatch = (m_df['A1'] != m_df['ALT1'])
        m_df['A1_FREQ'] = np.abs(a1_mismatch - m_df['ALT1_FREQ'])

        # Estimate BETA:
        m_df['BETA'] = compute_beta(m_df)

        # Estimate standard errors:
        m_df['SE'] = compute_se(m_df)

        # Compute p-values:
        m_df['P'] = 2.*stats.norm.sf(abs(m_df.Z.values))

        # Transform columns and column names:
        m_df = m_df[['#CHROM', 'POS', 'ID', 'A2', 'A1', 'A1', 'A1_FREQ', 'N', 'BETA', 'SE', 'Z', 'P']]
        m_df.columns = ['#CHROM', 'POS', 'ID', 'REF', 'ALT1', 'A1', 'A1_FREQ', 'OBS_CT', 'BETA', 'SE', 'T_STAT', 'P']

        # Output the file in the format of PLINK:

        chrom_name = osp.basename(freq_file).replace(".afreq", "")

        for i in range(1, 6):
            output_f = osp.join(args.genotype_dir.split('/')[0], "gwas",
                                trait_type, f"real_fold_{i}", trait_name, chrom_name + extension)
            makedir(osp.dirname(output_f))
            m_df.to_csv(output_f, index=False, sep="\t")


def separate_sumstats_by_chromosome(ss_df, trait_name, trait_type='quantitative'):

    ss_df.drop_duplicates(subset='ID', keep=False, inplace=True)

    for freq_file in glob.glob(osp.join(args.genotype_dir, "*.afreq")):
        freq_df = pd.read_csv(freq_file, delim_whitespace=True)

        m_df = freq_df.merge(ss_df, on='ID', suffixes=('_f', ''))

        # Transform columns and column names:
        m_df = m_df[['#CHROM', 'POS', 'ID', 'A2', 'A1', 'A1', 'A1_FREQ', 'OBS_CT', 'BETA', 'SE', 'T_STAT', 'P']]
        m_df.columns = ['#CHROM', 'POS', 'ID', 'REF', 'ALT1', 'A1', 'A1_FREQ', 'OBS_CT', 'BETA', 'SE', 'T_STAT', 'P']

        chrom_name = osp.basename(freq_file).replace(".afreq", "")

        if trait_type == 'quantitative':
            extension = ".PHENO1.glm.linear"
        else:
            extension = ".PHENO1.glm.logistic"

        for i in range(1, 6):
            output_f = osp.join(args.genotype_dir.split('/')[0], "gwas",
                                trait_type, f"real_fold_{i}", trait_name, chrom_name + extension)
            makedir(osp.dirname(output_f))
            m_df.to_csv(output_f, index=False, sep="\t")


def replicate_cross_validation_files(gwas_f):
    """
    Replicate the cross validation and phenotype files for the external GWAS trait
    from the corresponding internal GWAS traits.
    For example, if we have cross-validation files for height from
    the UKB, replicate those files for GWAS from an external cohort.
    :param gwas_f: The GWAS directory
    """

    trait = osp.basename(gwas_f).replace('.sumstats', '')
    ukb_trait = trait.split('_')[1]
    trait_type = gwas_f.split('/')[2]

    # Copy the cross-validation files:
    source = f"data/keep_files/ukbb_cv/{trait_type}/{ukb_trait}/"
    destination = f"data/keep_files/ukbb_cv/{trait_type}/{trait}/"

    if not osp.isdir(destination):
        shutil.copytree(source, destination)

    # Copy the phenotype files:
    source = f"data/phenotypes/{trait_type}/real/{ukb_trait}.txt"
    destination = f"data/phenotypes/{trait_type}/real/{trait}.txt"

    if not osp.isfile(destination):
        shutil.copy(source, destination)


# ----------------------------------------------------------------------------------------------------------------------


# Loop over the LDSC sumstats files and transform them:
for f in (glob.glob("data/external_gwas/*/PASS_*.sumstats") +
          glob.glob("data/external_gwas/*/UKB_*.sumstats")):
    print(f"> Transforming {f}")
    transform_ldsc_sumstats(f)
    replicate_cross_validation_files(f)

# ----------------------------------------------------------------------------------------------------------------------

print("> Transforming Wood_HEIGHT")

# Transform the HEIGHT summary statistics data from Wood et al. (GIANT)
# MarkerName	Allele1	Allele2	Freq.Allele1.HapMapCEU	b	SE	p	N
wood_height = pd.read_csv("data/external_gwas/quantitative/Wood_HEIGHT.sumstats",
                          delim_whitespace=True)

wood_height.rename(columns={
    'MarkerName': 'ID',
    'Allele1': 'A1',
    'Allele2': 'A2',
    'Freq.Allele1.HapMapCEU': 'A1_FREQ',
    'N': 'OBS_CT',
    'b': 'BETA',
    'p': 'P'
}, inplace=True)

wood_height['T_STAT'] = wood_height['BETA'] / wood_height['SE']

separate_sumstats_by_chromosome(wood_height, trait_name="Wood_HEIGHT")
replicate_cross_validation_files("data/external_gwas/quantitative/Wood_HEIGHT.sumstats")

# -------------------------------------------------------------

print("> Transforming Locke_BMI")

# Transform the BMI summary statistics data from Locke et al. (GIANT)
# to PLINK2-style summary statistics:

# SNP	A1	A2	Freq1.Hapmap	b	se	p	N
locke_bmi = pd.read_csv("data/external_gwas/quantitative/Locke_BMI.sumstats",
                        delim_whitespace=True)

locke_bmi.rename(columns={
    'SNP': 'ID',
    'Freq1.Hapmap': 'A1_FREQ',
    'N': 'OBS_CT',
    'b': 'BETA',
    'se': 'SE',
    'p': 'P'
}, inplace=True)

locke_bmi['T_STAT'] = locke_bmi['BETA'] / locke_bmi['SE']
separate_sumstats_by_chromosome(locke_bmi, trait_name="Locke_BMI")
replicate_cross_validation_files("data/external_gwas/quantitative/Locke_BMI.sumstats")

# -------------------------------------------------------------

"""
print("> Transforming Yengo_BMI")

# Transform the BMI meta-analyzed summary statistics data from Yengo et al.
# to PLINK2-style summary statistics:

# CHR	POS	SNP	Tested_Allele	Other_Allele	Freq_Tested_Allele_in_HRS	BETA	SE	P	N
yengo_bmi = pd.read_csv("data/external_gwas/quantitative/Yengo_BMI.sumstats",
                        delim_whitespace=True)

yengo_bmi.rename(columns={
    'SNP': 'ID',
    'Tested_Allele': 'A1',
    'Other_Allele': 'A2',
    'Freq_Tested_Allele_in_HRS': 'A1_FREQ',
    'N': 'OBS_CT'
}, inplace=True)

yengo_bmi['T_STAT'] = yengo_bmi['BETA'] / yengo_bmi['SE']

separate_sumstats_by_chromosome(yengo_bmi, trait_name="Yengo_BMI")
replicate_cross_validation_files("data/external_gwas/quantitative/Yengo_BMI.sumstats")

# -------------------------------------------------------------

print("> Transforming Yengo_HEIGHT")

# Transform the HEIGHT meta-analyzed summary statistics data from Yengo et al.
# to PLINK2-style summary statistics:

# CHR	POS	SNP	Tested_Allele	Other_Allele	Freq_Tested_Allele_in_HRS	BETA	SE	P	N
yengo_height = pd.read_csv("data/external_gwas/quantitative/Yengo_HEIGHT.sumstats",
                           delim_whitespace=True)

yengo_height.rename(columns={
    'SNP': 'ID',
    'Tested_Allele': 'A1',
    'Other_Allele': 'A2',
    'Freq_Tested_Allele_in_HRS': 'A1_FREQ',
    'N': 'OBS_CT'
}, inplace=True)

yengo_height['T_STAT'] = yengo_height['BETA'] / yengo_height['SE']

separate_sumstats_by_chromosome(yengo_height, trait_name="Yengo_HEIGHT")
replicate_cross_validation_files("data/external_gwas/quantitative/Yengo_HEIGHT.sumstats")
"""
