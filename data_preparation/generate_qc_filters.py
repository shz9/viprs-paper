"""
Author: Shadi Zabad
Date: April 2021
"""

import os
import glob
import errno
import os.path as osp
import pandas as pd


# ----------- Options -----------

# *** Sample options ***:
n_ld_samples = 50000  # Number of samples used to compute LD matrices
perc_training = 0.8  # Proportion of samples used for training (excluding samples used for LD)
num_pcs = 10  # Number of PCs to use as covariates (must be less than 40!)

# File names:
covar_file = "data/covariates/covar_file.txt"
keep_file = "data/keep_files/ukbb_qc_individuals.keep"
ld_keep_file = "data/keep_files/ukbb_ld_subset.keep"
train_keep_file = "data/keep_files/ukbb_train_subset.keep"
test_keep_file = "data/keep_files/ukbb_test_subset.keep"

# *** Variant options ***:

min_info_score = 0.3
hapmap_3_snps = "data/keep_files/hm3_no_MHC.csv.bz2"  # Set to None in case we don't want to filter to HapMap3 SNPs.

variant_keep_file = "data/keep_files/ukbb_qc_variants.keep"


# ----------- Helpler functions -----------
def makedir(directory):
    try:
        os.makedirs(directory)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


# -------- Sample quality control --------
# Read the sample QC file from the UKBB archive
ind_list = pd.read_csv("/lustre03/project/6004777/projects/uk_biobank/lists/ukb_sqc_v2_fullID_head.txt", sep="\s+")

# Apply the standard filters:

ind_list = ind_list.loc[(ind_list['IID'] > 0) &  # Remove redacted samples
                        (ind_list['in.white.British.ancestry.subset'] == 1) &  # Keep only White British
                        (ind_list['used.in.pca.calculation'] == 1) &  # Keep samples used in PCA calculation
                        (ind_list['in.Phasing.Input.chr1_22'] == 1) &  # Keep samples used in phasing
                        (ind_list['excess.relatives'] == 0) &  # Remove samples with excess relatives
                        (ind_list['putative.sex.chromosome.aneuploidy'] == 0)  # Remove samples with sex chr aneuploidy
                        ]


# Write the list of remaining individuals to file:
makedir(osp.dirname(keep_file))
ind_list[['FID', 'IID']].to_csv(keep_file, sep="\t", header=False, index=False)

# -------- Sample covariate file --------
# Create a covariates file to use in GWAS:

pc_columns = ['PC' + str(i + 1) for i in range(num_pcs)]

# Need this file to get the age of the participant:
ind_data = pd.read_csv("/lustre03/project/6004777/projects/uk_biobank/raw/ukb4940.csv")
ind_data = ind_data[['eid', '21003-0.0']]
ind_data.columns = ['IID', 'age']

covar_df = pd.merge(ind_list[['FID', 'IID', 'Inferred.Gender'] + pc_columns],
                    ind_data)
# Fix the representation for a couple of columns:
covar_df['Inferred.Gender'] = covar_df['Inferred.Gender'].map({'M': 1, 'F': 0})

for col in pc_columns:
    covar_df[col] = covar_df[col].round(decimals=5)

# Write the file:
makedir(osp.dirname(covar_file))
covar_df.to_csv(covar_file, sep="\t", header=False, index=False)

# -------- Split samples to training/testing/ld --------

ind_list = ind_list[['FID', 'IID']]

# Select the subset of individuals that will be used for
# computing LD matrices:
ld_subset = ind_list.sample(n=n_ld_samples, random_state=1)

# Write to file:
makedir(osp.dirname(ld_keep_file))
ld_subset.to_csv(ld_keep_file, sep="\t", header=False, index=False)

# Remove individuals selected for LD computation:
train_test_subset = ind_list.loc[~ind_list['IID'].isin(ld_subset['IID'])]

# Select subset of individuals that will be used for training the model

train_subset = train_test_subset.sample(n=int(perc_training*len(train_test_subset)), random_state=1)

# Write to file:
makedir(osp.dirname(train_keep_file))
train_subset.to_csv(train_keep_file, sep="\t", header=False, index=False)

# Select subset of individuals that will be used for testing/validation:

test_subset = train_test_subset.loc[~train_test_subset['IID'].isin(train_subset['IID'])]

# Write to file:
makedir(osp.dirname(test_keep_file))
test_subset.to_csv(test_keep_file, sep="\t", header=False, index=False)

# ---------------- Variant QC ----------------

info_files = "/lustre03/project/6004777/projects/uk_biobank/imputed_data/full_UKBB/v3_snp_stats/ukb_mfi_chr*_v3.txt"

variant_df = pd.concat([pd.read_csv(f, sep="\t", header=None)[[1, 7]]
                        for f in glob.glob(info_files)])
variant_df.columns = ['SNP', 'INFO']

# Exclude variants with imputation score less than `min_info_score`
variant_df = variant_df.loc[variant_df['INFO'] >= min_info_score]

# Merge with HapMap3 filter if provided:
if hapmap_3_snps is not None:
    hm3_snps = pd.read_csv(hapmap_3_snps)
    variant_df = pd.merge(variant_df, hm3_snps)

# Write to file:
makedir(osp.dirname(variant_keep_file))
variant_df['SNP'].to_csv(variant_keep_file, header=False, index=False)
