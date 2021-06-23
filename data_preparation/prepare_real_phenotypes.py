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

pheno_file = "/lustre03/project/6004777/projects/uk_biobank/raw/ukb5602.csv"
keep_file = "data/keep_files/ukbb_qc_individuals.keep"

phenotypes = {
    "Waist circumference": "48-0.0",
    "Hip circumference": "49-0.0",
    "Standing height": "50-0.0",
    "Birth weight": "20022-0.0",
    "BMI": "21001-0.0"
}

keep_ind = pd.read_csv(keep_file, names=["FID", "IID"], sep="\t")
pheno_df = pd.read_csv(pheno_file)

pheno_df = keep_ind.merge(pheno_df[["eid"] + list(phenotypes.values())],
                          left_on="IID", right_on="eid")
pheno_df.drop('eid', axis=1, inplace=True)

# Write the phenotype files:
makedir("data/phenotypes/real/")

# Waist circumference:

wc = pheno_df[['FID', 'IID', '48-0.0']]
wc.columns = ['FID', 'IID', 'phenotype']
wc['phenotype'] = np.log(wc['phenotype'])
wc['phenotype'][wc['phenotype'] < 3.5] = np.nan
wc.to_csv("data/phenotypes/real/WC.txt", sep="\t")

# Hip circumference:

hc = pheno_df[['FID', 'IID', '49-0.0']]
hc.columns = ['FID', 'IID', 'phenotype']
hc['phenotype'] = np.log(hc['phenotype'])
hc['phenotype'][hc['phenotype'] < 4] = np.nan
hc.to_csv("data/phenotypes/real/HC.txt", sep="\t")

# Standing height:

sh = pheno_df[['FID', 'IID', '50-0.0']]
sh.columns = ['FID', 'IID', 'phenotype']
sh['phenotype'][sh['phenotype'] < 130] = np.nan
sh.to_csv("data/phenotypes/real/HEIGHT.txt", sep="\t")

# Birth weight:

bw = pheno_df[['FID', 'IID', '20022-0.0']]
bw.columns = ['FID', 'IID', 'phenotype']
bw['phenotype'][bw['phenotype'] < 1 | bw['phenotype'] > 6] = np.nan
bw.to_csv("data/phenotypes/real/BW.txt", sep="\t")

# BMI:

bmi = pheno_df[['FID', 'IID', '21001-0.0']]
bmi.columns = ['FID', 'IID', 'phenotype']
bmi['phenotype'] = np.log(bmi['phenotype'])
bmi.to_csv("data/phenotypes/real/BMI.txt", sep="\t")
