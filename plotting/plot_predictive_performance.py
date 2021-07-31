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
import functools
print = functools.partial(print, flush=True)


print("> Plotting predictive performance for different PRS methods...")

pred_metrics = ['R2', 'Alt R2', 'Full R2', 'Naive R2', 'Pearson Correlation', 'Partial Correlation']

simulation_dfs = []
real_dfs = []

for f in glob.glob("data/evaluation/*/*.csv"):

    config = osp.basename(osp.dirname(f))
    df = pd.read_csv(f)

    if 'real' in config:
        real_dfs.append(df)
    else:
        simulation_dfs.append(df)


sns.set_style("darkgrid")
sns.set_context("paper")

if len(simulation_dfs) > 0:
    print("> Plotting predictive performance on simulations...")

    final_simulation_df = pd.concat(simulation_dfs)

    for ld_panel in final_simulation_df['LD Panel'].unique():

        if ld_panel == 'external':
            continue

        s_df = final_simulation_df.loc[final_simulation_df['LD Panel'].isin([ld_panel, 'external'])]

        for metric in pred_metrics:
            plt.figure(figsize=(9, 6))
            g = sns.catplot(x="Heritability", y=metric,
                            hue="Model", col="Prop. Causal",
                            data=s_df, kind="box", showfliers=False)

            makedir(f"plots/predictive_performance/simulation/{ld_panel}")
            plt.savefig(f"plots/predictive_performance/simulation/{ld_panel}/{metric}_predictive_performance.pdf".replace(" ", "_"),
                        bbox_inches='tight')
            plt.close()


if len(real_dfs) > 0:
    print("> Plotting predictive performance on real data...")
    final_real_df = pd.concat(real_dfs)

    for ld_panel in final_real_df['LD Panel'].unique():

        if ld_panel == 'external':
            continue

        r_df = final_real_df.loc[final_real_df['LD Panel'].isin([ld_panel, 'external'])]

        for metric in pred_metrics:
            plt.figure(figsize=(9, 6))
            g = sns.catplot(x="Model", y=metric, col="Trait",
                            data=r_df, kind="box", col_wrap=4, showfliers=False)

            makedir(f"plots/predictive_performance/real/{ld_panel}")
            plt.savefig(f"plots/predictive_performance/real/{ld_panel}/{metric}_predictive_performance.pdf".replace(" ", "_"),
                        bbox_inches='tight')
            plt.close()
