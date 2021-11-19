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
covar_df = pd.read_csv("data/covariates/covar_file.txt",
                       names=["FID", "IID"] + covariates,
                       sep="\t")