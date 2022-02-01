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
from plot_utils import *
import seaborn as sns
from utils import makedir
import functools
import argparse
print = functools.partial(print, flush=True)


# ---------------------- Helper functions ----------------------

def extract_predictive_evaluation_data(phenotype_type=None,
                                       configuration=None,
                                       keep_models=None,
                                       keep_panels=None,
                                       keep_traits=None):
    """
    Extract evaluation metrics from files and combine them for plotting
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

    dfs = []

    for f in glob.glob(f"data/evaluation/{phenotype_type}/{configuration}/*.csv"):

        df = pd.read_csv(f)

        if keep_models is not None:
            df = df.loc[df['Model'].isin(keep_models), ]

        if keep_panels is not None:
            df = df.loc[df['LD Panel'].isin(keep_panels), ]

        dfs.append(df)

    if len(dfs) > 0:

        combined_df = pd.concat(dfs)

        if keep_traits is not None:
            combined_df = combined_df.loc[combined_df['Trait'].isin(keep_traits), ]

        return combined_df


def plot_simulation_predictive_performance(s_df, metric='R2',
                                           showfliers=False, model_order=None,
                                           palette='Set2'):

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

    return g


def plot_real_predictive_performance(r_df, metric='R2',
                                     add_bar_labels=True,
                                     x_label_rotation=90,
                                     hide_x_labels=False,
                                     model_order=None, row_order=None, col_order=None,
                                     col_wrap=3, palette='Set2'):

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

    if metric == 'ROC-AUC':
        for fig_ax in g.fig.axes:
            fig_ax.set_ylim(.5, 1.)

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

    parser = argparse.ArgumentParser(description='Plot predictive performance')
    parser.add_argument('-m', '--models', dest='models', type=str)
    parser.add_argument('-t', '--type', dest='type', type=str, default='quantitative',
                        choices={'quantitative', 'binary'},
                        help='The type of phenotype to consider')
    parser.add_argument('--rename', dest='rename', action='store_false', default=True,
                        help='Rename the models if necessary')
    parser.add_argument('--prefix', dest='prefix', type=str)
    parser.add_argument('--extension', dest='ext', type=str, default='eps')
    args = parser.parse_args()

    print("> Plotting predictive performance for different PRS methods...")

    if args.type == 'binary':
        pred_metrics = ['ROC-AUC', 'Average Precision', 'PR-AUC']
    else:
        pred_metrics = ['R2', 'Alt R2', 'Full R2', 'Naive R2', 'Pearson Correlation', 'Partial Correlation']

    final_simulation_df = extract_predictive_evaluation_data(phenotype_type=args.type,
                                                             configuration='simulation',
                                                             keep_models=args.models.split(","))
    final_real_df = extract_predictive_evaluation_data(phenotype_type=args.type,
                                                       configuration='real',
                                                       keep_models=args.models.split(","))

    sns.set_style("darkgrid")
    sns.set_context("paper")

    if final_simulation_df is not None:
        print("> Plotting predictive performance on simulations...")

        # Update the names of the model for final display in the plot:
        if args.rename:
            final_simulation_df = update_model_names(final_simulation_df)

        for ld_panel in final_simulation_df['LD Panel'].unique():

            if ld_panel == 'external':
                continue

            s_df = final_simulation_df.loc[final_simulation_df['LD Panel'].isin([ld_panel, 'external'])]

            if args.rename:
                model_order = sort_models(s_df['Model'].unique())
            else:
                model_order = s_df['Model'].unique()

            for metric in pred_metrics:
                plt.figure(figsize=set_figure_size('paper'))
                plot_simulation_predictive_performance(s_df, metric=metric,
                                                       model_order=model_order)

                if args.prefix is None:
                    final_output_dir = f"plots/predictive_performance/{args.type}/simulation/{ld_panel}"
                else:
                    final_output_dir = f"plots/predictive_performance/{args.type}/simulation/{ld_panel}/{args.prefix}"

                makedir(final_output_dir)
                plt.savefig(osp.join(final_output_dir, f"{metric}".replace(" ", "_") + "." + args.ext),
                            bbox_inches='tight')
                plt.close()

    if final_real_df is not None:
        print("> Plotting predictive performance on real data...")

        # Update the names of the model for final display in the plot:
        if args.rename:
            final_real_df = update_model_names(final_real_df)

        trait_order = sort_traits(args.type, final_real_df['Trait'].unique())

        for ld_panel in final_real_df['LD Panel'].unique():

            if ld_panel == 'external':
                continue

            r_df = final_real_df.loc[final_real_df['LD Panel'].isin([ld_panel, 'external'])]

            if args.rename:
                model_order = sort_models(r_df['Model'].unique())
            else:
                model_order = r_df['Model'].unique()

            for metric in pred_metrics:
                fig = plt.figure(figsize=set_figure_size('paper'))

                plot_real_predictive_performance(r_df, metric=metric,
                                                 model_order=model_order, row_order=trait_order, col_order=trait_order)

                if args.prefix is None:
                    final_output_dir = f"plots/predictive_performance/{args.type}/real/{ld_panel}"
                else:
                    final_output_dir = f"plots/predictive_performance/{args.type}/real/{ld_panel}/{args.prefix}"

                makedir(final_output_dir)
                plt.savefig(osp.join(final_output_dir, f"{metric}".replace(" ", "_") + "." + args.ext),
                            bbox_inches='tight')
                plt.close()


if __name__ == '__main__':
    main()
