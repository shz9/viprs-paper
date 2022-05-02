"""
Author: Shadi Zabad

NOTE: The transformations/filters applied here are derived from
 the following links (Thanks Florian!):

Quantitative traits:
https://github.com/privefl/UKBB-PGS/blob/main/code/prepare-pheno-fields.R
Binary traits:
https://github.com/privefl/paper-ldpred2/blob/master/code/prepare-phenotypes.R

"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from scipy.stats import rankdata, norm, zscore
import os.path as osp
import sys
import itertools
sys.path.append(osp.dirname(osp.dirname(__file__)))
from utils import makedir

input_dir = "/lustre03/project/6004777/projects/uk_biobank/raw/"
covariates = ['Sex'] + ['PC' + str(i + 1) for i in range(10)] + ['Age']

# Read the covariates file:
covar_df = pd.read_csv("data/covariates/covar_file_minority.txt",
                       names=["FID", "IID"] + covariates,
                       sep="\t")


# ------------------------------------------------------
# Quantitative phenotypes

file_q_trait_dict = {
    "ukb5602.csv": ["48-0.0", "49-0.0", "50-0.0", "3062-0.0", "3063-0.0", "20022-0.0", "21001-0.0"],
    "ukb27843.csv": ["30760-0.0", "30780-0.0"]
}

# Construct the phenotype table:
pheno_df = None

for ph_file, traits in file_q_trait_dict.items():
    df = pd.read_csv(osp.join(input_dir, ph_file))[["eid"] + traits]
    if pheno_df is None:
        pheno_df = df
    else:
        pheno_df = pheno_df.merge(df, on="eid")

pheno_df = covar_df[['FID', 'IID']].merge(pheno_df, left_on="IID", right_on="eid")
pheno_df.drop('eid', axis=1, inplace=True)

# Create the phenotype directory:
makedir("data/phenotypes_minority/quantitative/real/")

# Waist circumference:

wc = pheno_df[['FID', 'IID', '48-0.0']]
wc.columns = ['FID', 'IID', 'phenotype']
wc['phenotype'] = np.log(wc['phenotype'])
wc['phenotype'][wc['phenotype'] < 3.5] = np.nan
wc.to_csv("data/phenotypes_minority/quantitative/real/WC.txt", sep="\t", index=False, header=False, na_rep='NA')

# Hip circumference:

hc = pheno_df[['FID', 'IID', '49-0.0']]
hc.columns = ['FID', 'IID', 'phenotype']
hc['phenotype'] = np.log(hc['phenotype'])
hc['phenotype'][hc['phenotype'] < 4] = np.nan
hc.to_csv("data/phenotypes_minority/quantitative/real/HC.txt", sep="\t", index=False, header=False, na_rep='NA')

# Standing height:

sh = pheno_df[['FID', 'IID', '50-0.0']]
sh.columns = ['FID', 'IID', 'phenotype']
sh['phenotype'][sh['phenotype'] < 130] = np.nan
sh.to_csv("data/phenotypes_minority/quantitative/real/HEIGHT.txt", sep="\t", index=False, header=False, na_rep='NA')

# Birth weight:

bw = pheno_df[['FID', 'IID', '20022-0.0']]
bw.columns = ['FID', 'IID', 'phenotype']
bw['phenotype'][(bw['phenotype'] < 1) | (bw['phenotype'] > 6)] = np.nan
bw.to_csv("data/phenotypes_minority/quantitative/real/BW.txt", sep="\t", index=False, header=False, na_rep='NA')

# BMI:

bmi = pheno_df[['FID', 'IID', '21001-0.0']]
bmi.columns = ['FID', 'IID', 'phenotype']
bmi['phenotype'] = np.log(bmi['phenotype'])
bmi.to_csv("data/phenotypes_minority/quantitative/real/BMI.txt", sep="\t", index=False, header=False, na_rep='NA')

# HDL:

hdl = pheno_df[['FID', 'IID', '30760-0.0']]
hdl.columns = ['FID', 'IID', 'phenotype']
hdl['phenotype'] = np.log(hdl['phenotype'])
hdl.to_csv("data/phenotypes_minority/quantitative/real/HDL.txt", sep="\t", index=False, header=False, na_rep='NA')

# LDL:

ldl = pheno_df[['FID', 'IID', '30780-0.0']]
ldl.columns = ['FID', 'IID', 'phenotype']
ldl.to_csv("data/phenotypes_minority/quantitative/real/LDL.txt", sep="\t", index=False, header=False, na_rep='NA')

# FVC:

fvc = pheno_df[['FID', 'IID', '3062-0.0']]
fvc.columns = ['FID', 'IID', 'phenotype']
fvc['phenotype'][np.log(fvc['phenotype']) < -.5] = np.nan
fvc.to_csv("data/phenotypes_minority/quantitative/real/FVC.txt", sep="\t", index=False, header=False, na_rep='NA')

# FEV1

fev1 = pheno_df[['FID', 'IID', '3063-0.0']]
fev1.columns = ['FID', 'IID', 'phenotype']
fev1['phenotype'][np.log(fev1['phenotype']) < -1] = np.nan
fev1.to_csv("data/phenotypes_minority/quantitative/real/FEV1.txt", sep="\t", index=False, header=False, na_rep='NA')

# ------------------------------------------------------
# Case/control phenotypes

icd10_file = "ukb5922.csv"
illness_file = "ukb4940.csv"

# Add ICD10 cause of death, primary + secondary
icd10_cols = [f"40001-{i}.0" for i in range(2)] + [f"40002-{i}.{j}" for i, j in itertools.product(range(2), range(14))]
# Add ICD10 diagnoses, main + secondary
icd10_cols += [f"41202-0.{i}" for i in range(377)] + [f"41204-0.{i}" for i in range(344)]
general_illness_cols = [f"20002-{i}.{j}" for i, j in itertools.product(range(2), range(29))]

# Read the files and merge them:
df_icd10 = pd.read_csv(osp.join(input_dir, icd10_file),
                       usecols=['eid'] + icd10_cols)
df_illness = pd.read_csv(osp.join(input_dir, illness_file),
                         usecols=['eid'] + general_illness_cols)

df_disease = df_icd10.merge(df_illness, on="eid")

# Merge on the covariate file:
df_disease = covar_df[['FID', 'IID']].merge(df_disease, left_on="IID", right_on="eid")
df_disease.drop('eid', axis=1, inplace=True)

# Write the phenotype files:
makedir("data/phenotypes_minority/binary/real/")

# ------------------ Asthma ------------------

# Extract index of individuals who have been diagnosed with asthma
asthma_idx = np.where(np.logical_or(
    (df_disease[general_illness_cols] == 1111).any(axis=1),
    df_disease[icd10_cols].applymap(lambda x: str(x)[:3] == "J45").any(axis=1)
))[0]

# Extract index of individuals who have asthma-related diagnoses (to be excluded)
asthma_like_idx = np.where(np.logical_or(
    df_disease[general_illness_cols].applymap(lambda x: x in list(range(1111, 1126))).any(axis=1),
    df_disease[icd10_cols].applymap(lambda x: str(x)[:1] == "J").any(axis=1)
))[0]

asthma_df = df_disease[['FID', 'IID']]
asthma_df['phenotype'] = 0
asthma_df.values[asthma_like_idx, -1] = -9
asthma_df.values[asthma_idx, -1] = 1

asthma_df = asthma_df.loc[asthma_df['phenotype'] != -9]
asthma_df.to_csv("data/phenotypes_minority/binary/real/ASTHMA.txt", sep="\t", index=False, header=False, na_rep='NA')

# ------------------ T1D & T2D ------------------

# Extract index of individuals who have general diabetes diagnosis
diabetes_like_idx = np.where(np.logical_or(
    df_disease[general_illness_cols].applymap(lambda x: x in (1220, 1221, 1222, 1223)).any(axis=1),
    df_disease[icd10_cols].applymap(lambda x: str(x)[:3] in ("E10", "E11", "E12", "E13", "E14")).any(axis=1)
))[0]

# Extract index of individuals who have T1D diagnosis
t1d_idx = np.where(np.logical_or(
    (df_disease[general_illness_cols] == 1222).any(axis=1),
    df_disease[icd10_cols].applymap(lambda x: str(x)[:3] == "E10").any(axis=1)
))[0]

# Extract index of individuals who have T2D diagnosis
t2d_idx = np.where(np.logical_or(
    (df_disease[general_illness_cols] == 1223).any(axis=1),
    df_disease[icd10_cols].applymap(lambda x: str(x)[:3] == "E11").any(axis=1)
))[0]

# T1D:
t1d_df = df_disease[['FID', 'IID']]
t1d_df['phenotype'] = 0
t1d_df.values[diabetes_like_idx, -1] = -9
t1d_df.values[t1d_idx, -1] = 1
t1d_df.values[t2d_idx, -1] = -9

t1d_df = t1d_df.loc[t1d_df['phenotype'] != -9]
t1d_df.to_csv("data/phenotypes_minority/binary/real/T1D.txt", sep="\t", index=False, header=False, na_rep='NA')

# T2D:
t2d_df = df_disease[['FID', 'IID']]
t2d_df['phenotype'] = 0
t2d_df.values[diabetes_like_idx, -1] = -9
t2d_df.values[t2d_idx, -1] = 1
t2d_df.values[t1d_idx, -1] = -9

t2d_df = t2d_df.loc[t2d_df['phenotype'] != -9]
t2d_df.to_csv("data/phenotypes_minority/binary/real/T2D.txt", sep="\t", index=False, header=False, na_rep='NA')

# ------------------ RA ------------------

# Extract index of individuals who have been diagnosed with RA
ra_idx = np.where(np.logical_or(
    (df_disease[general_illness_cols] == 1464).any(axis=1),
    df_disease[icd10_cols].applymap(lambda x: str(x)[:3] in ("M05", "M06")).any(axis=1)
))[0]

# Extract index of individuals who have RA-related diagnoses (to be excluded)
ra_like_idx = np.where(np.logical_or(
    df_disease[general_illness_cols].applymap(lambda x: x in (1295, 1464, 1465, 1466, 1467, 1477, 1538)).any(axis=1),
    df_disease[icd10_cols].applymap(lambda x: str(x)[:1] == "M").any(axis=1)
))[0]

ra_df = df_disease[['FID', 'IID']]
ra_df['phenotype'] = 0
ra_df.values[ra_like_idx, -1] = -9
ra_df.values[ra_idx, -1] = 1

ra_df = ra_df.loc[ra_df['phenotype'] != -9]
ra_df.to_csv("data/phenotypes_minority/binary/real/RA.txt", sep="\t", index=False, header=False, na_rep='NA')

