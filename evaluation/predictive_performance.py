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

    pheno_df = pd.read_csv(trait_f, names=['FID', 'IID', 'phenotype'], delim_whitespace=True)
    trait_type, config, trait = trait_f.split("/")[2:]
    print("> Type:", trait_type, " | Configuration:", config, " | Trait:", trait)
    trait = trait.replace(".txt", "")

    if config == 'real':
        search_config = 'real_fold_*'
    else:
        search_config = config

    search_model = args.model.replace('all', '*')
    search_panel = args.panel.replace('all', '*')

    pheno_res = []

    for prs_file in glob.glob(f"data/test_scores/{search_panel}/{search_model}"
                              f"/{trait_type}/{search_config}/{trait}.prs"):

        ld_panel, model, _, m_config = prs_file.split("/")[2:6]
        print(f"> Evaluating {model} ({ld_panel})")

        prs_df = pd.read_csv(prs_file, delim_whitespace=True)

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
            'Class': ['Quantitative', 'Binary'][trait_type == 'binary']
        })
        if config == 'real':
            res.update({'Fold': int(m_config.replace('real_fold_', ''))})

        pheno_res.append(res)

    if len(pheno_res) < 1:
        return

    eval_pheno_df = pd.DataFrame(pheno_res)

    if config != 'real':
        _, h2, _, p = config.split("_")
        eval_pheno_df['Heritability'] = float(h2)
        eval_pheno_df['Prop. Causal'] = float(p)

    output_file = f"data/evaluation/{trait_type}/{config}/{trait}.csv"
    makedir(osp.dirname(output_file))

    if osp.isfile(output_file):
        # If the file already exists, load it and merge the new results:
        existing_df = pd.read_csv(output_file)
        existing_df['Trait'] = existing_df['Trait'].astype(str)

        # Specify the columns to merge on:
        merge_cols = ['Trait', 'LD Panel', 'Model', 'Class']
        if config == 'real':
            merge_cols += ['Fold']
        else:
            merge_cols += ['Heritability', 'Prop. Causal']

        # Merge existing and new evaluation datasets:
        eval_pheno_df = existing_df.merge(eval_pheno_df, how='outer', on=merge_cols)

        # Update the dataframe to keep newer results:
        for c in [col for col in eval_pheno_df.columns if '_y' in col]:
            eval_pheno_df[c.replace('_y', '')] = eval_pheno_df[c].fillna(eval_pheno_df[c.replace('_y', '_x')])
            eval_pheno_df.drop([c, c.replace('_y', '_x')], axis=1, inplace=True)

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
    parser.add_argument('-t', '--type', dest='type', type=str, default='all',
                        choices={'quantitative', 'binary', 'all'},
                        help='The type of phenotype to consider')
    parser.add_argument('-m', '--model', dest='model', type=str, default='all')
    parser.add_argument('-l', '--panel', dest='panel', type=str, default='ukbb_50k_windowed',
                        choices={'external', '1000G_sample', '1000G_shrinkage', '1000G_windowed', '1000G_block',
                                 'ukbb_1k_sample', 'ukbb_1k_shrinkage', 'ukbb_1k_windowed', 'ukbb_1k_block',
                                 'ukbb_10k_sample', 'ukbb_10k_shrinkage', 'ukbb_10k_windowed', 'ukbb_10k_block',
                                 'ukbb_50k_sample', 'ukbb_50k_shrinkage', 'ukbb_50k_windowed', 'ukbb_50k_block',
                                 'all'})
    args = parser.parse_args()

    if args.type == 'all':
        pheno_dir = f"data/phenotypes/*"
    else:
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
                           delim_whitespace=True)

    pool = Pool(4)
    pool.map(process_trait, glob.glob(pheno_dir))
    pool.close()
    pool.join()

    print("Done!")
