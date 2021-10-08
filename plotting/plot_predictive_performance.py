"""
Author: Shadi Zabad
Date: May 2021
"""

import pandas as pd
import glob
import os.path as osp
import sys
sys.path.append(osp.dirname(osp.dirname(__file__)))
import matplotlib.pyplot as plt
from plot_utils import add_labels_to_bars, update_model_names
import seaborn as sns
from utils import makedir
import functools
import argparse
print = functools.partial(print, flush=True)


parser = argparse.ArgumentParser(description='Plot predictive performance')
parser.add_argument('-m', '--models', dest='models', type=str)
parser.add_argument('--prefix', dest='prefix', type=str)
parser.add_argument('--extension', dest='ext', type=str, default='eps')
args = parser.parse_args()

print("> Plotting predictive performance for different PRS methods...")

pred_metrics = ['R2', 'Alt R2', 'Full R2', 'Naive R2', 'Pearson Correlation', 'Partial Correlation']
order = [
    'VIPRS',
    'VIPRSSBayes',
    'VIPRS-GS', 'VIPRS-GSv', 'VIPRS-GSl', 'VIPRS-GSvl',
    'VIPRS-BO', 'VIPRS-BOv',
    'VIPRS-BMA',
    'SBayesR',
    'Lassosum',
    'LDPred2-inf', 'LDPred2-auto', 'LDPred2-grid',
    'PRScs',
    'PRSice2',
]
trait_order = [
    'HEIGHT', 'HDL', 'BMI',
    'FVC', 'FEV1', 'HC',
    'WC', 'LDL', 'BW',
    'ASTHMA', 'T2D', 'T1D', 'RA'
]

# TODO: Put quantitative and binary phenotypes in separate panels.

simulation_dfs = []
real_dfs = []

for f in glob.glob("data/evaluation/*/*/*.csv"):

    config = osp.basename(osp.dirname(f))
    df = pd.read_csv(f)

    if args.models is not None:
        df = df.loc[df['Model'].isin(args.models.split(",")), ]

    if 'real' in config:
        real_dfs.append(df)
    else:
        simulation_dfs.append(df)


sns.set_style("darkgrid")
sns.set_context("paper")

if len(simulation_dfs) > 0:
    print("> Plotting predictive performance on simulations...")

    final_simulation_df = pd.concat(simulation_dfs)

    # Update the names of the model for final display in the plot:
    final_simulation_df = update_model_names(final_simulation_df)

    for ld_panel in final_simulation_df['LD Panel'].unique():

        if ld_panel == 'external':
            continue

        s_df = final_simulation_df.loc[final_simulation_df['LD Panel'].isin([ld_panel, 'external'])]
        model_order = [m for m in order if m in s_df['Model'].unique()]

        for metric in pred_metrics:
            plt.figure(figsize=(9, 6))
            g = sns.catplot(x="Heritability", y=metric,
                            hue="Model",
                            col="Prop. Causal",
                            row="Class",
                            data=s_df, kind="box",
                            showfliers=False,
                            hue_order=model_order,
                            palette='Set2')

            if args.prefix is None:
                final_output_dir = f"plots/predictive_performance/simulation/{ld_panel}"
            else:
                final_output_dir = f"plots/predictive_performance/simulation/{ld_panel}/{args.prefix}"

            makedir(final_output_dir)
            plt.savefig(osp.join(final_output_dir, f"{metric}".replace(" ", "_") + "." + args.ext),
                        bbox_inches='tight')
            plt.close()


if len(real_dfs) > 0:
    print("> Plotting predictive performance on real data...")
    final_real_df = pd.concat(real_dfs)

    # Update the names of the model for final display in the plot:
    final_real_df = update_model_names(final_real_df)

    for ld_panel in final_real_df['LD Panel'].unique():

        if ld_panel == 'external':
            continue

        r_df = final_real_df.loc[final_real_df['LD Panel'].isin([ld_panel, 'external'])]
        model_order = [m for m in order if m in r_df['Model'].unique()]

        for metric in pred_metrics:
            fig = plt.figure(figsize=(9, 6))
            g = sns.catplot(x="Model", y=metric, col="Trait",
                            data=r_df, kind="bar", col_wrap=4,
                            order=model_order,
                            row_order=trait_order,
                            col_order=trait_order,
                            palette='Set2')
            add_labels_to_bars(g)

            for i, ax in enumerate(g.fig.axes):
                ax.set_xticklabels(ax.get_xticklabels(), rotation=90)

            if args.prefix is None:
                final_output_dir = f"plots/predictive_performance/real/{ld_panel}"
            else:
                final_output_dir = f"plots/predictive_performance/real/{ld_panel}/{args.prefix}"

            makedir(final_output_dir)
            plt.savefig(osp.join(final_output_dir, f"{metric}".replace(" ", "_") + "." + args.ext),
                        bbox_inches='tight')
            plt.close()
