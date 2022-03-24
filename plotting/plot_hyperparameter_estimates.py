"""
Author: Shadi Zabad
Date: May 2021
"""

import pandas as pd
import numpy as np
import glob
import os.path as osp
import sys
sys.path.append(osp.dirname(osp.dirname(__file__)))
import matplotlib.pyplot as plt
import seaborn as sns
from utils import makedir
import argparse
import functools
print = functools.partial(print, flush=True)
from plot_utils import *


def extract_hyperparameter_estimates_data(phenotype_type=None,
                                          configuration=None,
                                          keep_models=None,
                                          keep_panels=None,
                                          keep_traits=None):
    """
    Extract hyperparameter estimates from files and combine them for plotting
    :param phenotype_type: Can be `quantitative`, `binary`, or None (both)
    :param configuration: Can be `real`, `simulation`, or None (both)
    :param keep_models: Only keep a subset of the models
    :param keep_panels: The LD reference panel to use
    :param keep_traits: Extract data for only a subset of traits.
    """

    if phenotype_type is None:
        phenotype_type = '*'

    if configuration is None:
        configuration = '*'
    elif configuration == 'simulation':
        configuration = 'h2_*'
    else:
        configuration = 'real_fold_*'

    dfs = []

    for f in glob.glob(f"data/model_fit/*/*/{phenotype_type}/{configuration}/*/combined.hyp.gz"):

        _, _, ld_panel, model, trait_type, config, trait, _ = f.split("/")

        if keep_models is not None:
            if model not in keep_models:
                continue

        if keep_panels is not None:
            if ld_panel not in keep_panels:
                continue

        if keep_traits is not None:
            if trait not in keep_traits:
                continue

        if model == 'SBayesR':
            df = pd.read_csv(f, header=0, names=['Parameter', 'data'])
            df['Value'] = df.data.str.split("\t").str[0].astype(float)
        else:
            df = pd.read_csv(f, sep="\t")

        est_h2g = df.loc[df.Parameter == 'Heritability', 'Value'].sum()

        if model == 'SBayesR':
            est_p = df.loc[df.Parameter == 'Prop. Causal', 'Value'].mean()
        else:
            est_p = df.loc[df.Parameter == 'Proportion_causal', 'Value'].mean()

        est_df = pd.DataFrame({'Model': [model], 'Trait': [trait],
                               'Estimated Heritability': [est_h2g],
                               'Estimated Prop. Causal': [est_p]})

        if 'real' in config:
            est_df['Heritability'] = np.nan
            est_df['Prop. Causal'] = np.nan
        else:
            _, h2, _, p = config.split("_")
            est_df['Heritability'] = float(h2)
            est_df['Prop. Causal'] = float(p)

        dfs.append(est_df)

    if len(dfs) >= 1:
        return pd.concat(dfs)


def plot_simulation_hyperparameter_estimates(s_df, metric,
                                             showfliers=False,
                                             model_order=None,
                                             palette='Set2',
                                             log_scale=False):

    assert metric in ('Estimated Heritability', 'Estimated Prop. Causal')

    g = sns.catplot(x="Heritability",
                    y=metric,
                    hue="Model",
                    col="Prop. Causal",
                    data=s_df,
                    kind="box",
                    showfliers=showfliers,
                    hue_order=model_order,
                    palette=palette)

    if metric_name is not None:
        g.set_axis_labels("Heritability", metric_name(metric))

    if log_scale:
        for i, ax in enumerate(g.fig.axes):
            ax.set_yscale('log', base=10)

    return g


def plot_real_hyperparameter_estimates(r_df, metric,
                                       add_bar_labels=True,
                                       x_label_rotation=90,
                                       hide_x_labels=False,
                                       model_order=None, row_order=None, col_order=None,
                                       col_wrap=3, palette='Set2',
                                       log_scale=False):

    assert metric in ('Estimated Heritability', 'Estimated Prop. Causal')

    g = sns.catplot(x="Model",
                    y=metric,
                    col="Trait",
                    data=r_df,
                    kind="bar",
                    col_wrap=col_wrap,
                    order=model_order,
                    row_order=row_order,
                    col_order=col_order,
                    palette=palette)

    if log_scale:
        for i, ax in enumerate(g.fig.axes):
            ax.set_ylim(ymin=r_df[metric].min())
            ax.set_yscale('log', base=10)

    if add_bar_labels:
        add_labels_to_bars(g)

    if x_label_rotation != 0 or hide_x_labels:
        for fig_ax in g.fig.axes:
            if hide_x_labels:
                fig_ax.set_xticklabels([])
            else:
                fig_ax.set_xticklabels(fig_ax.get_xticklabels(), rotation=x_label_rotation)

    # Update the subplot titles:
    for fig_ax in g.fig.axes:
        fig_ax.set_title(fig_ax.get_title().replace("Trait = ", ""))

    if metric_name is not None:
        g.set_axis_labels("Model", metric_name(metric))

    return g

# ---------------------------------------------------------------


def main():

    parser = argparse.ArgumentParser(description='Plot hyperparameter estimates')
    parser.add_argument('-l', '--ld-panel', dest='ld_panel', type=str, default='ukbb_50k_windowed')
    parser.add_argument('--extension', dest='ext', type=str, default='eps')
    parser.add_argument('-t', '--type', dest='type', type=str, default='quantitative',
                        choices={'quantitative', 'binary'},
                        help='The type of phenotype to consider')
    args = parser.parse_args()

    print(f"> Plotting hyperparameter estimates for {args.type} traits...")

    simulation_data = extract_hyperparameter_estimates_data(phenotype_type=args.type,
                                                            keep_models=['VIPRS', 'SBayesR'],
                                                            configuration='simulation',
                                                            keep_panels=['external', args.ld_panel])
    real_data = extract_hyperparameter_estimates_data(phenotype_type=args.type,
                                                      configuration='real',
                                                      keep_models=['VIPRS', 'SBayesR'],
                                                      keep_traits=['HEIGHT', 'HDL', 'BMI',
                                                                   'FVC', 'FEV1', 'HC',
                                                                   'WC', 'LDL', 'BW'],
                                                      keep_panels=['external', args.ld_panel])

    sns.set_style("darkgrid")
    sns.set_context("paper")

    if len(simulation_data) > 0:
        print("> Plotting hyperparameter estimates on simulated data...")

        plt.figure(figsize=(9, 6))
        plot_simulation_hyperparameter_estimates(simulation_data, metric='Estimated Heritability',
                                                 model_order=sort_models(simulation_data['Model'].unique()))

        makedir(f"plots/hyperparameters/{args.type}/simulation/h2g/")
        plt.savefig(f"plots/hyperparameters/{args.type}/simulation/h2g/{args.ld_panel}_estimates." + args.ext,
                    bbox_inches='tight')
        plt.close()

        plt.figure(figsize=(9, 6))
        plot_simulation_hyperparameter_estimates(simulation_data, metric='Estimated Prop. Causal',
                                                 model_order=sort_models(simulation_data['Model'].unique()),
                                                 log_scale=True)
        makedir(f"plots/hyperparameters/{args.type}/simulation/pi/")
        plt.savefig(f"plots/hyperparameters/{args.type}/simulation/pi/{args.ld_panel}_estimates." + args.ext,
                    bbox_inches='tight')
        plt.close()

    if len(real_data) > 0:
        print("> Plotting hyperparameter estimates on real data...")

        plt.figure(figsize=(9, 6))
        trait_order = sort_traits(args.type, real_data['Trait'].unique())

        plot_real_hyperparameter_estimates(real_data, "Estimated Heritability",
                                           col_wrap=[3, 1][args.type == 'binary'],
                                           model_order=sort_models(simulation_data['Model'].unique()),
                                           row_order=trait_order, col_order=trait_order)

        makedir(f"plots/hyperparameters/{args.type}/real/h2g/")
        plt.savefig(f"plots/hyperparameters/{args.type}/real/h2g/{args.ld_panel}_estimates." + args.ext,
                    bbox_inches='tight')
        plt.close()

        plt.figure(figsize=(9, 6))
        plot_real_hyperparameter_estimates(real_data, "Estimated Prop. Causal",
                                           col_wrap=[3, 1][args.type == 'binary'],
                                           model_order=sort_models(simulation_data['Model'].unique()),
                                           row_order=trait_order, col_order=trait_order,
                                           log_scale=True)
        makedir(f"plots/hyperparameters/{args.type}/real/pi/")
        plt.savefig(f"plots/hyperparameters/{args.type}/real/pi/{args.ld_panel}_estimates." + args.ext,
                    bbox_inches='tight')
        plt.close()


if __name__ == '__main__':
    main()
