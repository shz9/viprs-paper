"""
Author: Shadi Zabad
Date: April 2021
"""

import sys
import os.path as osp
sys.path.append(osp.dirname(osp.dirname(__file__)))
import glob
import numpy as np
import pandas as pd
from utils import makedir
import functools
print = functools.partial(print, flush=True)


# ----------- Options -----------

# *** Sample options ***:

# Number of samples used to compute LD matrices
n_ld_samples = 50000
n_ld_subsamples = [10000, 1000]  # Subsamples of the 50k individuals used to compute LD

# Whether the individuals selected for the LD reference panel can be in the training/testing/validation sets.
overlapping_ld = False
# Proportion of samples used for training, validation, and testing
train, valid, test = .7, .15, .15
# Number of PCs to include as covariates (must be less than 40!)
num_pcs = 10

# File names:
covar_file = "data/covariates/covar_file.txt"
keep_file = "data/keep_files/ukbb_qc_individuals.keep"

ld_keep_file = "data/keep_files/ukbb_ld_{}_subset.keep"
train_keep_file = "data/keep_files/ukbb_train_subset.keep"
valid_keep_file = "data/keep_files/ukbb_valid_subset.keep"
test_keep_file = "data/keep_files/ukbb_test_subset.keep"

# *** Variant options ***:

min_info_score = 0.3
hapmap_3_snps = "metadata/hm3_no_MHC.csv.bz2"  # Set to None in case we don't want to filter to HapMap3 SNPs.

variant_keep_file = "data/keep_files/ukbb_qc_variants.keep"
variant_hm3_keep_file = "data/keep_files/ukbb_qc_variants_hm3.keep"


# -------- Sample quality control --------
# Read the sample QC file from the UKBB archive
print("> Extracting individuals with white British ancestry...")

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

print("Creating a file with covariates for the selected individuals...")

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

# ------------------------------------------------------
# -------- Split samples to training/validation/testing/ld --------
# ------------------------------------------------------

print("> Splitting the data to training/validation/testing/ld subsets...")

def humanize_number(n):
    if n >= 1000:
        return str(int(n / 1000)) + 'k'
    else:
        return str(n)


ind_list = ind_list[['FID', 'IID']]

# Select the subset of individuals that will be used for
# computing LD matrices:
ld_subset = ind_list.sample(n=n_ld_samples, random_state=1)

# Write to file:
makedir(osp.dirname(ld_keep_file))
ld_subset.to_csv(ld_keep_file.format(humanize_number(n_ld_samples)),
                 sep="\t", header=False, index=False)

# For smaller sample sizes of the LD panel, write their keep files as well:
for subsample_n in n_ld_subsamples:
    ld_subset_subsample = ld_subset.sample(n=subsample_n, random_state=1)

    # Write to file:
    makedir(osp.dirname(ld_keep_file))
    ld_subset_subsample.to_csv(ld_keep_file.format(humanize_number(subsample_n)),
                               sep="\t", header=False, index=False)

# If the LD samples should not be overlapping with training set, remove from list:
if overlapping_ld:
    tvt_subset = ind_list  # Train/validation/test subset
else:
    tvt_subset = ind_list.loc[~ind_list['IID'].isin(ld_subset['IID'])]

# Get the indices of the training/validation/testing sets and shuffle them:
ind_index = tvt_subset.index.values
np.random.shuffle(ind_index)

# Obtain the indices for each subset:
training_subset = ind_index[:int(train*len(ind_index))]
validation_subset = ind_index[int(train*len(ind_index)): int((train + valid)*len(ind_index))]
testing_subset = ind_index[int((train + valid)*len(ind_index)):]

# Finally, output a keep file of the individuals in each subset:

# (1) The training subset:
makedir(osp.dirname(train_keep_file))
tvt_subset.loc[training_subset].to_csv(train_keep_file, sep="\t", header=False, index=False)

# (2) The validation subset:
makedir(osp.dirname(valid_keep_file))
tvt_subset.loc[validation_subset].to_csv(valid_keep_file, sep="\t", header=False, index=False)

# (3) The testing subset:
makedir(osp.dirname(test_keep_file))
tvt_subset.loc[testing_subset].to_csv(test_keep_file, sep="\t", header=False, index=False)

# --------------------------------------------
# ---------------- Variant QC ----------------
# --------------------------------------------

print("> Performing variant filtering and selection...")

info_files = "/lustre03/project/6004777/projects/uk_biobank/imputed_data/full_UKBB/v3_snp_stats/ukb_mfi_chr*_v3.txt"

# Read the long-range LD regions dataframe:
lr_ld_df = pd.read_csv("metadata/long_range_ld.txt", sep="\s+")

# Read the SNP information:
v_dfs = []
for f in glob.glob(info_files):

    try:
        vdf = pd.read_csv(f, sep="\t",
                          names=['ID', 'SNP', 'POS', 'A1', 'A2', 'MAF', 'MinorAllele', 'INFO'])

        # Extract the chromosome information from the file name:
        chrom = int(f.split('_')[-2].replace('chr', ''))
        vdf['CHR'] = chrom
        v_dfs.append(vdf)
    except Exception as e:
        print(e)
        continue

variant_df = pd.concat(v_dfs)

# Exclude all SNPs with duplicate IDs:
# IMPORTANT: This must be done before any filtering!
variant_df = variant_df.drop_duplicates(subset='SNP', keep=False)

# Exclude variants with imputation score less than `min_info_score`
variant_df = variant_df.loc[variant_df['INFO'] >= min_info_score]

# Exclude all SNPs with ambiguous strand (A/T or G/C):
variant_df = variant_df.loc[
    ~(
        ((variant_df['A1'] == 'A') & (variant_df['A2'] == 'T')) |
        ((variant_df['A1'] == 'T') & (variant_df['A2'] == 'A')) |
        ((variant_df['A1'] == 'G') & (variant_df['A2'] == 'C')) |
        ((variant_df['A1'] == 'C') & (variant_df['A2'] == 'G'))
    )
]

# Exclude SNPs in long-range LD regions:
snp_lr_ld = variant_df.merge(lr_ld_df, on='CHR')
snp_lr_ld = snp_lr_ld.loc[(snp_lr_ld['POS'] >= snp_lr_ld['StartPosition']) &
                          (snp_lr_ld['POS'] <= snp_lr_ld['EndPosition']), ['SNP']]
snp_lr_ld = snp_lr_ld.drop_duplicates(subset='SNP', keep=False)

variant_df = variant_df.loc[~variant_df['SNP'].isin(snp_lr_ld['SNP'])]

# Write to file:
makedir(osp.dirname(variant_keep_file))
variant_df['SNP'].to_csv(variant_keep_file, header=False, index=False)

# Merge with HapMap3 filter if provided:
if hapmap_3_snps is not None:
    hm3_snps = pd.read_csv(hapmap_3_snps)
    variant_df = pd.merge(variant_df, hm3_snps)

    # Write to file:
    makedir(osp.dirname(variant_hm3_keep_file))
    variant_df['SNP'].to_csv(variant_hm3_keep_file, header=False, index=False)
