from plot_utils import *
import numpy as np
import pandas as pd
import os.path as osp
import sys
sys.path.append(osp.dirname(osp.dirname(__file__)))
from utils import makedir
import glob
import argparse
import seaborn as sns
import matplotlib.pyplot as plt


def compute_trait_prs_corr(trait_f, configuration, keep_models=None, keep_ld_panels=None):

    pheno_df = pd.read_csv(trait_f, names=['FID', 'IID', 'phenotype'], delim_whitespace=True)

    trait_type, config, trait = trait_f.split("/")[2:]
    print("> Type:", trait_type, " | Configuration:", config, " | Trait:", trait)
    trait = trait.replace(".txt", "")

    pheno_df.rename(columns={'phenotype': trait}, inplace=True)

    merged_df = pheno_df

    for prs_file in glob.glob(f"data/test_scores/*/*/{trait_type}/{configuration}/{trait}.prs"):

        ld_panel, model, _, m_config = prs_file.split("/")[2:6]

        if keep_models is not None:
            if model not in keep_models:
                continue

        if keep_ld_panels is not None:
            if ld_panel not in keep_ld_panels:
                continue

        prs_df = pd.read_csv(prs_file, delim_whitespace=True)
        prs_df.rename(columns={'PRS': 'PRS_' + model}, inplace=True)

        merged_df = merged_df.merge(prs_df).dropna()

    merged_df.drop(columns=['FID', 'IID'], inplace=True)
    merged_df = (merged_df - merged_df.mean()) / merged_df.std()
    merged_df['PRS_Avg'] = merged_df[['PRS_' + c for c in combined_models]].mean(axis=1)

    return merged_df.corr()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Generate Figure 1')
    parser.add_argument('--extension', dest='ext', type=str, default='eps')
    args = parser.parse_args()

    combined_models = ['VIPRS-GSv_p', 'SBayesR']
    keep_models = ['VIPRS', 'VIPRS-GSv_p', 'SBayesR', 'Lassosum', 'LDPred2-grid', 'PRScs', 'PRSice2']
    keep_panels = ['external', 'ukbb_50k_windowed']
    real_traits = glob.glob("data/phenotypes/*/real/*.txt")
    real_folds = [f'real_fold_{i}' for i in range(1, 6)]

    sns.set_context("paper", font_scale=.9)
    makedir("plots/supplementary/prs_correlation/")

    for trait in real_traits:

        trait_name = osp.basename(trait).replace('.txt', '')

        trait_corr_mat = None

        for fold in real_folds:
            if trait_corr_mat is None:
                trait_corr_mat = compute_trait_prs_corr(trait, fold,
                                                        keep_models=keep_models, keep_ld_panels=keep_panels)
            else:
                trait_corr_mat += compute_trait_prs_corr(trait, fold,
                                                         keep_models=keep_models, keep_ld_panels=keep_panels)

        trait_corr_mat /= len(real_folds)

        # Plot the correlation matrix:
        f, ax = plt.subplots(figsize=set_figure_size('paper'))
        mask = np.triu(np.ones_like(trait_corr_mat, dtype=bool))

        sns.heatmap(trait_corr_mat, mask=mask, cmap="crest",
                    annot=True, fmt='.3f', annot_kws={"fontsize": 7},
                    square=True, linewidths=.5)

        plt.savefig(f"plots/supplementary/prs_correlation/{trait_name}." + args.ext, bbox_inches='tight')
        plt.close()
