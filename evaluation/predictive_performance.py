import pandas as pd
import numpy as np
import statsmodels.api as sm
import glob
import os.path as osp
import sys
sys.path.append(osp.dirname(osp.dirname(__file__)))
from utils import makedir
import functools
print = functools.partial(print, flush=True)


def evaluate_predictive_performance(model_df):

    null_result = sm.OLS(model_df['phenotype'], sm.add_constant(model_df[covariates])).fit()
    full_result = sm.OLS(model_df['phenotype'], sm.add_constant(model_df[covariates + ['PRS']])).fit()

    # Naive R2, regress the PRS on the phenotype:
    naive_result = sm.OLS(model_df['phenotype'], sm.add_constant(model_df[['PRS']])).fit()

    # Used to compute partial correlation:
    prs_result = sm.OLS(model_df['PRS'], sm.add_constant(model_df[covariates])).fit()

    return {
        'Null R2': null_result.rsquared,
        'Full R2': full_result.rsquared,
        'R2': full_result.rsquared - null_result.rsquared,
        'Naive R2': naive_result.rsquared,
        'Alt R2': 1. - np.sum(full_result.resid**2)/np.sum(null_result.resid**2),
        'Pearson Correlation': np.corrcoef(model_df['phenotype'], model_df['PRS'])[0, 1],
        'Partial Correlation': np.corrcoef(null_result.resid, prs_result.resid)[0, 1]
    }


print("> Evaluating predictive performance of PRS methods...")

# Covariates:
covariates = ['Sex'] + ['PC' + str(i + 1) for i in range(10)] + ['Age']

# Read the covariates file:
covar_df = pd.read_csv("data/covariates/covar_file.txt",
                       names=['FID', 'IID'] + covariates,
                       sep="\s+")

for trait_f in glob.glob("data/phenotypes/*/*.txt"):

    pheno_df = pd.read_csv(trait_f, names=['FID', 'IID', 'phenotype'], sep="\s+")
    config, trait = trait_f.split("/")[2:]
    print("> Configuration:", config, " | Trait:", trait)
    trait = trait.replace(".txt", "")

    if config == 'real':
        search_config = 'real_fold_*'
    else:
        search_config = config

    pheno_res = []

    for prs_file in glob.glob(f"data/test_scores/*/*/{search_config}/{trait}.prs"):

        ld_panel, model, m_config = prs_file.split("/")[2:5]
        print(f"> Evaluating {model} ({ld_panel})")

        prs_df = pd.read_csv(prs_file, sep="\s+")

        prs_df = prs_df.reset_index()

        merged_df = pheno_df.merge(prs_df).dropna()
        merged_df = merged_df.merge(covar_df).dropna()

        res = evaluate_predictive_performance(merged_df)
        res.update({
            'Trait': trait,
            'LD Panel': ld_panel,
            'Model': model,
        })
        if config == 'real':
            res.update({'Fold': int(m_config.replace('real_fold_', ''))})

        pheno_res.append(res)

    eval_pheno_df = pd.DataFrame(pheno_res)

    if config != 'real':
        _, h2, _, p = config.split("_")
        eval_pheno_df['Heritability'] = float(h2)
        eval_pheno_df['Prop. Causal'] = float(p)

    makedir(f"data/evaluation/{config}/")
    eval_pheno_df.to_csv(f"data/evaluation/{config}/{trait}.csv", index=False)

