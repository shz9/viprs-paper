"""
Author: Shadi Zabad

NOTE: The transformations/filters applied here are derived from:
https://github.com/privefl/UKBB-PGS/blob/main/code/prepare-pheno-fields.R
"""

import pandas as pd
import numpy as np
import os.path as osp
import sys
sys.path.append(osp.dirname(osp.dirname(__file__)))
from utils import makedir

input_dir = "/lustre03/project/6004777/projects/uk_biobank/raw/"

file_pheno_dict = {
    "ukb5602.csv": ["48-0.0", "49-0.0", "50-0.0", "20022-0.0", "21001-0.0"],
    "ukb27843.csv": ["30760-0.0", "30780-0.0"]
}
keep_file = "data/keep_files/ukbb_qc_individuals.keep"

phenotypes = {
    "Waist circumference": "48-0.0",
    "Hip circumference": "49-0.0",
    "Standing height": "50-0.0",
    "Birth weight": "20022-0.0",
    "BMI": "21001-0.0",
    "HDL": "30760-0.0",
    "LDL": "30780-0.0"
}

keep_ind = pd.read_csv(keep_file, names=["FID", "IID"], sep="\t")

pheno_df = None

for ph_file, traits in file_pheno_dict.items():
    df = pd.read_csv(osp.join(input_dir, ph_file))[["eid"] + traits]
    if pheno_df is None:
        pheno_df = df
    else:
        pheno_df = pheno_df.merge(df, on="eid")

pheno_df = keep_ind.merge(pheno_df, left_on="IID", right_on="eid")
pheno_df.drop('eid', axis=1, inplace=True)

# Write the phenotype files:
makedir("data/phenotypes/real/")

# Waist circumference:

wc = pheno_df[['FID', 'IID', '48-0.0']]
wc.columns = ['FID', 'IID', 'phenotype']
wc['phenotype'] = np.log(wc['phenotype'])
wc['phenotype'][wc['phenotype'] < 3.5] = np.nan
wc.to_csv("data/phenotypes/real/WC.txt", sep="\t", index=False, header=False, na_rep='NA')

# Hip circumference:

hc = pheno_df[['FID', 'IID', '49-0.0']]
hc.columns = ['FID', 'IID', 'phenotype']
hc['phenotype'] = np.log(hc['phenotype'])
hc['phenotype'][hc['phenotype'] < 4] = np.nan
hc.to_csv("data/phenotypes/real/HC.txt", sep="\t", index=False, header=False, na_rep='NA')

# Standing height:

sh = pheno_df[['FID', 'IID', '50-0.0']]
sh.columns = ['FID', 'IID', 'phenotype']
sh['phenotype'][sh['phenotype'] < 130] = np.nan
sh.to_csv("data/phenotypes/real/HEIGHT.txt", sep="\t", index=False, header=False, na_rep='NA')

# Birth weight:

bw = pheno_df[['FID', 'IID', '20022-0.0']]
bw.columns = ['FID', 'IID', 'phenotype']
bw['phenotype'][(bw['phenotype'] < 1) | (bw['phenotype'] > 6)] = np.nan
bw.to_csv("data/phenotypes/real/BW.txt", sep="\t", index=False, header=False, na_rep='NA')

# BMI:

bmi = pheno_df[['FID', 'IID', '21001-0.0']]
bmi.columns = ['FID', 'IID', 'phenotype']
bmi['phenotype'] = np.log(bmi['phenotype'])
bmi.to_csv("data/phenotypes/real/BMI.txt", sep="\t", index=False, header=False, na_rep='NA')

# HDL:

hdl = pheno_df[['FID', 'IID', '30760-0.0']]
hdl.columns = ['FID', 'IID', 'phenotype']
hdl['phenotype'] = np.log(hdl['phenotype'])
hdl.to_csv("data/phenotypes/real/HDL.txt", sep="\t", index=False, header=False, na_rep='NA')

# LDL:

ldl = pheno_df[['FID', 'IID', '30780-0.0']]
ldl.columns = ['FID', 'IID', 'phenotype']
ldl.to_csv("data/phenotypes/real/LDL.txt", sep="\t", index=False, header=False, na_rep='NA')
