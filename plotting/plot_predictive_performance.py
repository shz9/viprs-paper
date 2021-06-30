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

simulation_dfs = []
real_dfs = []

for f in glob.glob(f"data/evaluation/*/*.csv"):

    config = osp.basename(osp.dirname(f))
    df = pd.read_csv(f)

    if config == 'real':
        real_dfs.append(df)
    else:
        simulation_dfs.append(df)


if len(simulation_dfs) > 0:
    print("> Plotting predictive performance on simulations...")

    final_simulation_df = pd.concat(simulation_dfs)

    for ld_panel in final_simulation_df['LD Panel'].unique():

        s_df = final_simulation_df.loc[final_simulation_df['LD Panel'] == ld_panel]
        plt.figure(figsize=(9, 6))
        g = sns.catplot(x="Heritability", y="R2",
                        hue="Model", col="Prop. Causal",
                        data=s_df, kind="box")

        makedir(f"plots/predictive_performance/simulation/")
        plt.savefig(f"plots/predictive_performance/simulation/{ld_panel}_predictive_performance.pdf",
                    bbox_inches='tight')
        plt.close()


if len(real_dfs) > 0:
    print("> Plotting predictive performance on real data...")
    final_real_df = pd.concat(real_dfs)

    for ld_panel in final_real_df['LD Panel'].unique():
        r_df = final_real_df.loc[final_real_df['LD Panel'] == ld_panel]
        plt.figure(figsize=(9, 6))
        g = sns.catplot(x="Model", y="R2",
                        hue="Model", col="Trait",
                        data=final_real_df, kind="bar")

        makedir(f"plots/predictive_performance/real/")
        plt.savefig(f"plots/predictive_performance/real/{ld_panel}_predictive_performance.pdf",
                    bbox_inches='tight')
        plt.close()
