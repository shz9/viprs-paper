import pandas as pd
import numpy as np
import statsmodels.api as sm
from sklearn.metrics import auc, average_precision_score, precision_recall_curve, roc_auc_score
import glob
import os.path as osp
import sys
sys.path.append(osp.dirname(osp.dirname(__file__)))
from utils import makedir
import argparse
import functools
from multiprocessing import Pool
print = functools.partial(print, flush=True)


def evaluate_gaussian_predictive_performance(model_df):

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


def evaluate_binomial_predictive_performance(model_df):

    prs_prob = 1./(1. + np.exp(-model_df['PRS'].values))
    y_true = model_df['phenotype'].values
    precision, recall, thresholds = precision_recall_curve(y_true, prs_prob)

    return {
        'ROC-AUC': roc_auc_score(y_true, prs_prob),
        'Average Precision': average_precision_score(y_true, prs_prob),
        'PR-AUC': auc(recall, precision)
    }


def process_trait(trait_f):

    pheno_df = pd.read_csv(trait_f, names=['FID', 'IID', 'phenotype'], sep="\s+")
    trait_type, config, trait = trait_f.split("/")[2:]
    print("> Configuration:", config, " | Trait:", trait)
    trait = trait.replace(".txt", "")

    if config == 'real':
        search_config = 'real_fold_*'
    else:
        search_config = config

    pheno_res = []

    for prs_file in glob.glob(f"data/test_scores/*/*/{trait_type}/{search_config}/{trait}.prs"):

        ld_panel, model, _, m_config = prs_file.split("/")[2:6]
        print(f"> Evaluating {model} ({ld_panel})")

        prs_df = pd.read_csv(prs_file, sep="\s+")

        prs_df = prs_df.reset_index()

        merged_df = pheno_df.merge(prs_df).dropna()
        merged_df = merged_df.merge(covar_df).dropna()

        if trait_type == 'binary':
            res = evaluate_binomial_predictive_performance(merged_df)
        else:
            res = evaluate_gaussian_predictive_performance(merged_df)

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

    makedir(f"data/evaluation/{trait_type}/{config}/")
    eval_pheno_df.to_csv(f"data/evaluation/{trait_type}/{config}/{trait}.csv", index=False)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Evaluate the predictive performance of PRS models')

    parser.add_argument('-p', '--phenotype', dest='pheno_name', type=str,
                        help='The name of the phenotype to evaluate.')
    parser.add_argument('-c', '--config', dest='config', type=str,
                        help='The simulation configuration to evaluate')
    parser.add_argument('-a', '--application', dest='application', type=str,
                        choices={'real', 'simulation'},
                        help='The category of phenotypes to consider')
    parser.add_argument('-t', '--type', dest='type', type=str, default='quantitative',
                        choices={'quantitative', 'binary'},
                        help='The type of phenotype to consider')
    args = parser.parse_args()

    pheno_dir = f"data/phenotypes/{args.type}"

    if args.pheno_name is not None:
        pheno_dir = osp.join(pheno_dir, "real", args.pheno_name + ".txt")
    elif args.config is not None:
        pheno_dir = osp.join(pheno_dir, args.config, "*.txt")
    elif args.application is not None:
        if args.application == 'real':
            pheno_dir = osp.join(pheno_dir, "real", "*.txt")
        else:
            pheno_dir = osp.join(pheno_dir, "h2_*", "*.txt")
    else:
        pheno_dir = osp.join(pheno_dir, "*", "*.txt")

    print("> Evaluating predictive performance of PRS methods...")

    # Covariates:
    covariates = ['Sex'] + ['PC' + str(i + 1) for i in range(10)] + ['Age']

    # Read the covariates file:
    covar_df = pd.read_csv("data/covariates/covar_file.txt",
                           names=['FID', 'IID'] + covariates,
                           sep="\s+")

    pool = Pool(4)
    pool.map(process_trait, glob.glob(pheno_dir))
    pool.close()
    pool.join()

    print("Done!")
