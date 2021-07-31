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
from plot_utils import add_labels_to_bars


parser = argparse.ArgumentParser(description='Plot hyperparameter estimates')
parser.add_argument('-l', '--ld-panel', dest='ld_panel', type=str, default='ukbb_50k_windowed')
args = parser.parse_args()

print("> Plotting hyperparameter estimates...")

simulation_dfs = []
real_dfs = []

for f in glob.glob(f"data/model_fit/{args.ld_panel}/*/*/*/combined.hyp") + \
         glob.glob(f"data/model_fit/external/*/*/*/combined.hyp"):

    _, _, _, model, config, trait, _ = f.split("/")

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
    final_simulation_df = final_simulation_df.groupby(['Heritability', 'Prop. Causal', 'Trait', 'Model']).agg(
        {'Estimated Heritability': 'sum', 'Estimated Prop. Causal': 'mean'}
    ).reset_index()

    plt.figure(figsize=(9, 6))
    g = sns.catplot(x="Heritability", y="Estimated Heritability",
                    hue="Model", col="Prop. Causal",
                    data=final_simulation_df, kind="box", showfliers=False)

    makedir("plots/hyperparameters/simulation/h2g/")
    plt.savefig(f"plots/hyperparameters/simulation/h2g/{args.ld_panel}_estimates.pdf", bbox_inches='tight')
    plt.close()

    plt.figure(figsize=(9, 6))
    g = sns.catplot(x="Prop. Causal", y="Estimated Prop. Causal",
                    hue="Model", col="Heritability",
                    data=final_simulation_df, kind="box", showfliers=False)
    makedir("plots/hyperparameters/simulation/pi/")
    plt.savefig(f"plots/hyperparameters/simulation/pi/{args.ld_panel}_estimates.pdf", bbox_inches='tight')
    plt.close()

if len(real_dfs) > 0:
    print("> Plotting hyperparameter estimates on real data...")

    final_real_df = pd.concat(real_dfs)

    plt.figure(figsize=(9, 6))
    g = sns.catplot(x="Model", y="Estimated Heritability", col="Trait", col_wrap=4,
                    data=final_real_df, kind="box", showfliers=False)

    makedir("plots/hyperparameters/real/h2g/")
    plt.savefig(f"plots/hyperparameters/real/h2g/{args.ld_panel}_estimates.pdf", bbox_inches='tight')
    plt.close()

    plt.figure(figsize=(9, 6))
    g = sns.catplot(x="Model", y="Estimated Prop. Causal", col="Trait", col_wrap=4,
                    data=final_real_df, kind="box", showfliers=False)
    makedir("plots/hyperparameters/real/pi/")
    plt.savefig(f"plots/hyperparameters/real/pi/{args.ld_panel}_estimates.pdf", bbox_inches='tight')
    plt.close()

