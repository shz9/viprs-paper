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


def extract_validation_data(phenotype_type=None,
                            configuration=None,
                            keep_models=None,
                            keep_panels=None,
                            keep_traits=None,
                            keep_chromosomes=None):
    """
    Extract validation data from files and combine them for plotting
    :param phenotype_type: Can be `quantitative`, `binary`, or None (both)
    :param configuration: Can be `real`, `simulation`, or None (both)
    :param keep_models: Only keep a subset of the models
    :param keep_panels: The LD reference panel to use
    :param keep_traits: Extract data for only a subset of traits.
    :param keep_chromosomes: Extract data for only a subset of the chromosomes
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

    for f in glob.glob(f"data/model_fit/*/*/{phenotype_type}/{configuration}/*/combined.validation.gz"):

        _, _, ld_panel, model, trait_type, config, trait, _ = f.split("/")

        if 'v_' not in model:
            continue

        if keep_models is not None:
            if model not in keep_models:
                continue

        if keep_panels is not None:
            if ld_panel not in keep_panels:
                continue

        if keep_traits is not None:
            if trait not in keep_traits:
                continue

        df = pd.read_csv(f, sep="\t")
        df['Trait'] = trait
        df['Model'] = model
        df['LD Panel'] = ld_panel

        if keep_chromosomes is not None:
            df = df.loc[df.CHR.isin(keep_chromosomes), ]

        if 'real' in config:
            df['Heritability'] = np.nan
            df['Prop. Causal'] = np.nan
        else:
            _, h2, _, p = config.split("_")
            df['Heritability'] = float(h2)
            df['Prop. Causal'] = float(p)

        dfs.append(df)

    if len(dfs) >= 1:
        return pd.concat(dfs)


def plot_validation_vs_elbo_scatter(data_df,
                                    col='Trait',
                                    col_wrap=3,
                                    sharex=False,
                                    sharey=False,
                                    col_order=None,
                                    row_order=None,
                                    x_bins=15,
                                    fit_reg=False):

    g = sns.lmplot(data=data_df,
                   x='ELBO',
                   y='Validation R2',
                   col=col,
                   col_order=col_order,
                   row_order=row_order,
                   col_wrap=col_wrap,
                   sharex=sharex,
                   sharey=sharey,
                   x_bins=x_bins,
                   fit_reg=fit_reg)

    # Ensures that the x-axis ticks are written in scientific notation:
    for ax in g.fig.axes:
        ax.ticklabel_format(style='sci', scilimits=(0, 0), axis='x')

    if col == 'Trait':
        # Update the subplot titles:
        for fig_ax in g.fig.axes:
            fig_ax.set_title(fig_ax.get_title().replace("Trait = ", ""))

    g.set_axis_labels("ELBO", "Validation $R^2$")

    return g


def main():

    parser = argparse.ArgumentParser(description='Plot validation results')
    parser.add_argument('--extension', dest='ext', type=str, default='eps')
    parser.add_argument('-t', '--type', dest='type', type=str, default='quantitative',
                        choices={'quantitative', 'binary'},
                        help='The type of phenotype to consider')
    parser.add_argument('--chromosome', dest='chromosome', type=str, default='chr_2',
                        help='Filter to the pre-specified chromosome')
    args = parser.parse_args()

    print(f"> Plotting validation for {args.type} traits...")

    real_validation_data = extract_validation_data(phenotype_type=args.type,
                                                   configuration='real',
                                                   keep_chromosomes=[args.chromosome],
                                                   keep_models=['VIPRS-GSv_p'])

    if len(real_validation_data) < 1:
        return

    sns.set_style("darkgrid")
    sns.set_context("paper", font_scale=1.8)

    plt.figure(figsize=set_figure_size(width='paper', subplots=(3, 5)))
    plot_validation_vs_elbo_scatter(real_validation_data,
                                    col_wrap=5,
                                    row_order=sort_traits(args.type, real_validation_data['Trait'].unique()),
                                    col_order=sort_traits(args.type, real_validation_data['Trait'].unique()))
    plt.subplots_adjust(wspace=.25)
    makedir(f"plots/supplementary/validation_vs_elbo/{args.type}/")
    plt.savefig(f"plots/supplementary/validation_vs_elbo/{args.type}/{args.chromosome}." + args.ext,
                bbox_inches='tight')
    plt.close()


if __name__ == '__main__':
    main()
