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
import seaborn as sns
from utils import makedir
import argparse
import functools
print = functools.partial(print, flush=True)
from plot_utils import update_model_names, real_trait_order


parser = argparse.ArgumentParser(description='Plot hyperparameter estimates')
parser.add_argument('-l', '--ld-panel', dest='ld_panel', type=str, default='ukbb_50k_windowed')
parser.add_argument('--extension', dest='ext', type=str, default='eps')
parser.add_argument('-t', '--type', dest='type', type=str, default='quantitative',
                    choices={'quantitative', 'binary'},
                    help='The type of phenotype to consider')
args = parser.parse_args()

order = [
    'VIPRS', 'VIPRSSBayes',
    'VIPRS-GS', 'VIPRS-GSv', 'VIPRS-GSl', 'VIPRS-GSvl',
    'VIPRS-BO', 'VIPRS-BOv',
    'SBayesR']
trait_order = real_trait_order(args.type)

print(f"> Plotting hyperparameter estimates for {args.type} traits...")

simulation_dfs = []
real_dfs = []

for f in glob.glob(f"data/model_fit/{args.ld_panel}/*/{args.type}/*/*/combined.hyp") + \
         glob.glob(f"data/model_fit/external/*/{args.type}/*/*/combined.hyp"):

    _, _, _, model, trait_type, config, trait, _ = f.split("/")

    df = pd.read_csv(f, index_col=0).T
    df.columns = ['Estimated ' + c for c in df.columns]

    df['Model'] = model
    df['Trait'] = trait

    if 'real' in config:
        real_dfs.append(df)
    else:

        _, h2, _, p = config.split("_")
        df['Heritability'] = float(h2)
        df['Prop. Causal'] = float(p)

        simulation_dfs.append(df)

sns.set_style("darkgrid")
sns.set_context("paper")

if len(simulation_dfs) > 0:
    print("> Plotting hyperparameter estimates on simulated data...")

    final_simulation_df = pd.concat(simulation_dfs)

    # Update model names:
    final_simulation_df = update_model_names(final_simulation_df)

    final_simulation_df = final_simulation_df.groupby(['Heritability', 'Prop. Causal', 'Trait', 'Model']).agg(
        {'Estimated Heritability': 'sum', 'Estimated Prop. Causal': 'mean'}
    ).reset_index()

    model_order = [m for m in order if m in final_simulation_df['Model'].unique()]

    plt.figure(figsize=(9, 6))
    g = sns.catplot(x="Heritability",
                    y="Estimated Heritability",
                    hue="Model", col="Prop. Causal",
                    data=final_simulation_df, kind="box", showfliers=False,
                    hue_order=model_order,
                    palette='Set2')

    makedir(f"plots/hyperparameters/{args.type}/simulation/h2g/")
    plt.savefig(f"plots/hyperparameters/{args.type}/simulation/h2g/{args.ld_panel}_estimates." + args.ext,
                bbox_inches='tight')
    plt.close()

    plt.figure(figsize=(9, 6))
    g = sns.catplot(x="Prop. Causal", y="Estimated Prop. Causal",
                    hue="Model", col="Heritability",
                    data=final_simulation_df, kind="box", showfliers=False,
                    hue_order=model_order,
                    palette='Set2')
    for i, ax in enumerate(g.fig.axes):
        ax.set_yscale('log')
    makedir(f"plots/hyperparameters/{args.type}/simulation/pi/")
    plt.savefig(f"plots/hyperparameters/{args.type}/simulation/pi/{args.ld_panel}_estimates." + args.ext,
                bbox_inches='tight')
    plt.close()

if len(real_dfs) > 0:
    print("> Plotting hyperparameter estimates on real data...")

    final_real_df = pd.concat(real_dfs)

    # Update model names:
    final_real_df = update_model_names(final_real_df)

    model_order = [m for m in order if m in final_real_df['Model'].unique()]

    plt.figure(figsize=(9, 6))
    g = sns.catplot(x="Model", y="Estimated Heritability", col="Trait", col_wrap=[3, 4][args.type == 'binary'],
                    data=final_real_df, kind="box", showfliers=False,
                    order=model_order, row_order=trait_order,
                    palette='Set2')
    for i, ax in enumerate(g.fig.axes):
        ax.set_xticklabels(ax.get_xticklabels(), rotation=90)

    makedir(f"plots/hyperparameters/{args.type}/real/h2g/")
    plt.savefig(f"plots/hyperparameters/{args.type}/real/h2g/{args.ld_panel}_estimates." + args.ext,
                bbox_inches='tight')
    plt.close()

    plt.figure(figsize=(9, 6))
    g = sns.catplot(x="Model", y="Estimated Prop. Causal", col="Trait", col_wrap=[3, 4][args.type == 'binary'],
                    data=final_real_df, kind="box", showfliers=False,
                    order=model_order,
                    row_order=trait_order,
                    palette='Set2')
    for i, ax in enumerate(g.fig.axes):
        ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
        ax.set_yscale('log')
    makedir(f"plots/hyperparameters/{args.type}/real/pi/")
    plt.savefig(f"plots/hyperparameters/{args.type}/real/pi/{args.ld_panel}_estimates." + args.ext,
                bbox_inches='tight')
    plt.close()

