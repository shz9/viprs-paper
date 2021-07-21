"""
Author: Shadi Zabad

NOTE: The transformations/filters applied here are derived from:
https://github.com/privefl/UKBB-PGS/blob/main/code/prepare-pheno-fields.R
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from scipy.stats import rankdata, norm, zscore
import os.path as osp
import sys
sys.path.append(osp.dirname(osp.dirname(__file__)))
from utils import makedir

input_dir = "/lustre03/project/6004777/projects/uk_biobank/raw/"
covariates = ['Sex'] + ['PC' + str(i + 1) for i in range(10)] + ['Age']

file_pheno_dict = {
    "ukb5602.csv": ["48-0.0", "49-0.0", "50-0.0", "3062-0.0", "3063-0.0", "20022-0.0", "21001-0.0"],
    "ukb27843.csv": ["30760-0.0", "30780-0.0"]
}

phenotypes = {
    "Waist circumference": "48-0.0",
    "Hip circumference": "49-0.0",
    "Standing height": "50-0.0",
    "Birth weight": "20022-0.0",
    "BMI": "21001-0.0",
    "HDL": "30760-0.0",
    "LDL": "30780-0.0",
    "FVC": "3062-0.0",
    "FEV1": "3063-0.0"
}


def transform_phenotype(phe_df, covar_df,
                        offset=3./8,
                        outlier_thres=5):
    """
    This function takes a phenotype dataframe and a covariates dataframe
    and applies covariate correction as well as Rank-based inverse normal transform
    on the phenotype.
    :param phe_df: The phenotype dataframe
    :param covar_df: The covariates dataframe
    :param covariates: The covariates to use for adjusting the phenotype.
    :param offset: The offset to use in the INT transformation (Blom's offset by default).
    :param outlier_thres: The threshold to remove outliers
    :return:
    """

    # Step 1: Merge the two dataframes and remove NAs:
    m_df = phe_df.merge(covar_df)
    m_df.dropna(inplace=True)

    fin_dfs = []

    # Step 2: For each sex, apply the transformation:
    for sex in m_df['Sex'].unique():

        sm_df = m_df.loc[m_df['Sex'] == sex]
        # Step 2.1: Perform covariate correction (excluding sex) and obtain residuals:
        phe_resid = sm.OLS(sm_df['phenotype'], sm.add_constant(sm_df[covariates[1:]])).fit().resid
        # Step 2.2: Rank the residuals:
        phe_resid_r = rankdata(phe_resid, method="average")
        # Step 2.3: Apply inverse normal transformation (using Blom's offset):
        phe_rint = norm.ppf((phe_resid_r - offset) / (len(phe_resid_r) - 2*offset + 1))
        # Step 2.4: Create a new dataframe with the transformed phenotype:
        final_phe = pd.DataFrame({'FID': sm_df['FID'].values, 'IID': sm_df['IID'].values, 'phenotype': phe_rint})
        # Step 2.5: Remove outliers:
        final_phe = final_phe.loc[(np.abs(zscore(final_phe['phenotype'])) < outlier_thres)]

        fin_dfs.append(final_phe)

    return pd.concat(fin_dfs)


# Read the covariates file:
covar_df = pd.read_csv("data/covariates/covar_file.txt",
                       names=["FID", "IID"] + covariates,
                       sep="\t")

# Construct the phenotype table:
pheno_df = None

for ph_file, traits in file_pheno_dict.items():
    df = pd.read_csv(osp.join(input_dir, ph_file))[["eid"] + traits]
    if pheno_df is None:
        pheno_df = df
    else:
        pheno_df = pheno_df.merge(df, on="eid")

pheno_df = covar_df[['FID', 'IID']].merge(pheno_df, left_on="IID", right_on="eid")
pheno_df.drop('eid', axis=1, inplace=True)

# Write the phenotype files:
makedir("data/phenotypes/real/")

# Waist circumference:

wc = pheno_df[['FID', 'IID', '48-0.0']]
wc.columns = ['FID', 'IID', 'phenotype']
wc['phenotype'] = np.log(wc['phenotype'])
wc['phenotype'][wc['phenotype'] < 3.5] = np.nan
wc = transform_phenotype(wc, covar_df)
wc.to_csv("data/phenotypes/real/WC.txt", sep="\t", index=False, header=False, na_rep='NA')

# Hip circumference:

hc = pheno_df[['FID', 'IID', '49-0.0']]
hc.columns = ['FID', 'IID', 'phenotype']
hc['phenotype'] = np.log(hc['phenotype'])
hc['phenotype'][hc['phenotype'] < 4] = np.nan
hc = transform_phenotype(hc, covar_df)
hc.to_csv("data/phenotypes/real/HC.txt", sep="\t", index=False, header=False, na_rep='NA')

# Standing height:

sh = pheno_df[['FID', 'IID', '50-0.0']]
sh.columns = ['FID', 'IID', 'phenotype']
sh['phenotype'][sh['phenotype'] < 130] = np.nan
sh = transform_phenotype(sh, covar_df)
sh.to_csv("data/phenotypes/real/HEIGHT.txt", sep="\t", index=False, header=False, na_rep='NA')

# Birth weight:

bw = pheno_df[['FID', 'IID', '20022-0.0']]
bw.columns = ['FID', 'IID', 'phenotype']
bw['phenotype'][(bw['phenotype'] < 1) | (bw['phenotype'] > 6)] = np.nan
bw = transform_phenotype(bw, covar_df)
bw.to_csv("data/phenotypes/real/BW.txt", sep="\t", index=False, header=False, na_rep='NA')

# BMI:

bmi = pheno_df[['FID', 'IID', '21001-0.0']]
bmi.columns = ['FID', 'IID', 'phenotype']
bmi['phenotype'] = np.log(bmi['phenotype'])
bmi = transform_phenotype(bmi, covar_df)
bmi.to_csv("data/phenotypes/real/BMI.txt", sep="\t", index=False, header=False, na_rep='NA')

# HDL:

hdl = pheno_df[['FID', 'IID', '30760-0.0']]
hdl.columns = ['FID', 'IID', 'phenotype']
hdl['phenotype'] = np.log(hdl['phenotype'])
hdl = transform_phenotype(hdl, covar_df)
hdl.to_csv("data/phenotypes/real/HDL.txt", sep="\t", index=False, header=False, na_rep='NA')

# LDL:

ldl = pheno_df[['FID', 'IID', '30780-0.0']]
ldl.columns = ['FID', 'IID', 'phenotype']
ldl = transform_phenotype(ldl, covar_df)
ldl.to_csv("data/phenotypes/real/LDL.txt", sep="\t", index=False, header=False, na_rep='NA')

# FVC:

fvc = pheno_df[['FID', 'IID', '3062-0.0']]
fvc.columns = ['FID', 'IID', 'phenotype']
fvc['phenotype'][np.log(fvc['phenotype']) < -.5] = np.nan
fvc = transform_phenotype(fvc, covar_df)
fvc.to_csv("data/phenotypes/real/FVC.txt", sep="\t", index=False, header=False, na_rep='NA')

# FEV1

fev1 = pheno_df[['FID', 'IID', '3063-0.0']]
fev1.columns = ['FID', 'IID', 'phenotype']
fev1['phenotype'][np.log(fev1['phenotype']) < -1] = np.nan
fev1 = transform_phenotype(fev1, covar_df)
fev1.to_csv("data/phenotypes/real/FEV1.txt", sep="\t", index=False, header=False, na_rep='NA')
