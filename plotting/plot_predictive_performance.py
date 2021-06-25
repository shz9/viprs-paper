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


parser = argparse.ArgumentParser(description='Plot predictive performance')
parser.add_argument('-l', '--ld-panel', dest='ld_panel', type=str, default='ukbb_50k_windowed')
args = parser.parse_args()

print("> Plotting predictive performance for different PRS methods...")

simulation_dfs = []
real_dfs = []

for f in glob.glob(f"data/evaluation/{args.ld_panel}/*/*.csv") + glob.glob(f"data/evaluation/external/*/*.csv"):

    config = osp.basename(osp.dirname(f))
    trait = osp.basename(f).replace(".csv", "")

    df = pd.read_csv(f)
    df['Trait'] = trait

    if config == 'real':
        real_dfs.append(df)
    else:

        _, h2, _, p = config.split("_")
        df['Heritability'] = float(h2)
        df['Prop. Causal'] = float(p)

        simulation_dfs.append(df)

if len(simulation_dfs) > 0:
    print("> Plotting predictive performance on simulations...")

    final_simulation_df = pd.concat(simulation_dfs)

    plt.figure(figsize=(9, 6))
    g = sns.catplot(x="Heritability", y="R2",
                    hue="Model", col="Prop. Causal",
                    data=final_simulation_df, kind="box")

    makedir(f"plots/predictive_performance/simulation/")
    plt.savefig(f"plots/predictive_performance/simulation/{args.ld_panel}_predictive_performance.pdf",
                bbox_inches='tight')
    plt.close()


if len(real_dfs) > 0:
    print("> Plotting predictive performance on real data...")
    final_real_df = pd.concat(real_dfs)

    plt.figure(figsize=(9, 6))
    g = sns.catplot(x="Model", y="R2",
                    hue="Model", col="Trait",
                    data=final_real_df, kind="bar")

    makedir(f"plots/predictive_performance/real/")
    plt.savefig(f"plots/predictive_performance/real/{args.ld_panel}_predictive_performance.pdf",
                bbox_inches='tight')
    plt.close()
