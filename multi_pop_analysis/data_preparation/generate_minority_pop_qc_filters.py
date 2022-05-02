import sys
import os.path as osp
from scipy.spatial.distance import pdist, squareform
sys.path.append(osp.dirname(osp.dirname(osp.dirname(__file__))))
import glob
import numpy as np
import pandas as pd
from utils import makedir
import functools
print = functools.partial(print, flush=True)


num_pcs = 10
keep_populations = ['Italy', 'India', 'China', 'Nigeria']

# File names:
covar_file = "data/covariates/covar_file_minority.txt"
keep_file = "data/keep_files/ukbb_qc_individuals_minority.keep"
ancestry_file = "data/covariates/ukbb_individual_ancestry.keep"

# ----------------------------------------

# Read the population geometric medians from Prive et al. 2022:
pop_list = pd.read_csv("metadata/pop_centers.txt")
num_pcs_pop_centers = len(pop_list.columns) - 1

# -------- Sample quality control --------
# Read the sample QC file from the UKBB archive
print("> Extracting individuals from minority populations...")

ind_list = pd.read_csv("/lustre03/project/6004777/projects/uk_biobank/lists/ukb_sqc_v2_fullID_head.txt", sep="\s+")

# Apply the standard filters:

ind_list = ind_list.loc[(ind_list['IID'] > 0) &  # Remove redacted samples
                        (ind_list['used.in.pca.calculation'] == 1) &  # Keep samples used in PCA calculation
                        (ind_list['in.Phasing.Input.chr1_22'] == 1) &  # Keep samples used in phasing
                        (ind_list['excess.relatives'] == 0) &  # Remove samples with excess relatives
                        (ind_list['putative.sex.chromosome.aneuploidy'] == 0),  # Remove samples with sex chr aneuploidy
                        ['FID', 'IID', 'Inferred.Gender'] +
                        [f'PC{i+1}' for i in range(max(num_pcs, num_pcs_pop_centers))]]

# The following steps are based on the following script by Prive et al. 2022:
# https://github.com/privefl/UKBB-PGS/blob/main/code/prepare-data.R
# Merge the list of individuals with the list of population centers and
# assign each individual to the population center closest to them:
mdf = ind_list.merge(pop_list, how='cross')
mdf['Euclidean_dist'] = ((mdf[[f'PC{i+1}_x' for i in range(num_pcs_pop_centers)]].values -
                          mdf[[f'PC{i+1}_y' for i in range(num_pcs_pop_centers)]].values)**2).sum(axis=1)
mdf = mdf.loc[mdf.groupby(['FID', 'IID'])['Euclidean_dist'].idxmin()]

# Compute the distances between the population centers to select a reasonable threshold
# for the distance between an individual and their nearest cluster:
distances = pdist(pop_list[[f'PC{i+1}' for i in range(num_pcs_pop_centers)]].values, metric='euclidean')
dist_matrix = squareform(distances)**2
thr_sq_dist = 0.002 * (dist_matrix.max() / 0.16)

# Individuals whose distance from the centers is greater than the threshold will have NAN ancestry:
mdf.loc[mdf['Euclidean_dist'] > thr_sq_dist, 'Ancestry'] = np.nan

# Finally, keep individuals whose ancestry in `keep_populations`
anc_df = mdf.loc[mdf['Ancestry'].isin(keep_populations), ['FID', 'IID', 'Ancestry']]
anc_df.to_csv(ancestry_file, sep="\t", index=False)

# Merge the ancestry dataframe on the original individual list:
ind_list = ind_list.merge(anc_df, on=['FID', 'IID'])

# Write the list of remaining individuals to file:
makedir(osp.dirname(keep_file))
ind_list[['FID', 'IID']].to_csv(keep_file, sep="\t", header=False, index=False)

# -------- Sample covariate file --------
# Create a covariates file to use in GWAS:

print("Creating a file with covariates for the selected individuals...")

pc_columns = [f'PC{i+1}' for i in range(num_pcs)]

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
