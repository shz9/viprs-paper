import pandas as pd
import matplotlib.pyplot as plt
import glob
import argparse
import seaborn as sns
from plot_utils import *
from sklearn.metrics import precision_recall_curve


def plot_precision_recall_curve(pr_df, trait_name):

    for m in sort_models(pr_df['Model'].unique()):
        sub_df = pr_df.loc[pr_df['Model'] == m, ]
        precision, recall, _ = precision_recall_curve(sub_df['phenotype'], sub_df['PRS'])
        plt.plot(recall, precision, label=m)

    plt.title(trait_name)
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.legend()


def extract_precision_recall_data(trait_f, keep_models=None, keep_panels=None):

    pheno_df = pd.read_csv(trait_f, names=['FID', 'IID', 'phenotype'], delim_whitespace=True)
    config, trait = trait_f.split("/")[3:]
    print("> Configuration:", config, " | Trait:", trait)
    trait = trait.replace(".txt", "")

    if config == 'real':
        search_config = 'real_fold_*'
    else:
        search_config = config

    pheno_res = []

    for prs_file in glob.glob(f"data/test_scores/*/*/binary/{search_config}/{trait}.prs.gz"):

        ld_panel, model, _, m_config = prs_file.split("/")[2:6]

        if keep_panels is not None:
            if ld_panel not in keep_panels:
                continue
        if keep_models is not None:
            if model not in keep_models:
                continue

        print(f"> Extracting data for {model} ({ld_panel})")

        prs_df = pd.read_csv(prs_file, delim_whitespace=True)

        merged_df = pheno_df.merge(prs_df).dropna()
        merged_df['Model'] = model
        merged_df['LD Panel'] = ld_panel

        pheno_res.append(merged_df)

    return pd.concat(pheno_res)


def main():

    parser = argparse.ArgumentParser(description='Generate Precision-Recall Curve Figures')
    parser.add_argument('--extension', dest='ext', type=str, default='eps')
    args = parser.parse_args()

    keep_models = ['VIPRS', 'VIPRS-GSv_p', 'SBayesR', 'Lassosum', 'LDPred2-grid', 'PRScs', 'PRSice2']
    keep_panels = ['external', 'ukbb_50k_windowed']

    for trait_file in glob.glob("data/phenotypes/binary/real/*.txt"):
        config, trait = trait_file.split("/")[3:]
        trait_name = trait.replace(".txt", "")

        trait_data = extract_precision_recall_data(trait_file, keep_models=keep_models, keep_panels=keep_panels)
        trait_data = update_model_names(trait_data)

        plt.figure(figsize=set_figure_size('paper'))
        plot_precision_recall_curve(trait_data, trait_name)
        plt.savefig(f"plots/supplementary/prc_curves/{trait_name}." + args.ext, bbox_inches='tight')
        plt.close()


if __name__ == '__main__':
    main()
