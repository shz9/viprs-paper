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

parser = argparse.ArgumentParser(description='Plot hyperparameter estimates')
parser.add_argument('-l', '--ld-panel', dest='ld_panel', type=str, default='ukbb_50k_windowed')
args = parser.parse_args()

dfs = []

for f in glob.glob(f"data/model_fit/{args.ld_panel}/*/*/*/chr_22.hyp") + glob.glob(f"data/model_fit/external/*/*/*/chr_22.hyp"):

    df = pd.read_csv(f, index_col=0).T
    df.columns = ['Estimated ' + c for c in df.columns]

    _, _, _, model, config, trait, _ = f.split("/")
    df['Trait'] = trait
    _, h2, _, p = config.split("_")
    df['Heritability'] = float(h2)
    df['Prop. Causal'] = float(p)
    df['Model'] = model

    dfs.append(df)

final_df = pd.concat(dfs)

plt.figure(figsize=(9, 6))
g = sns.catplot(x="Heritability", y="Estimated Heritability",
                hue="Model", col="Prop. Causal",
                data=final_df, kind="box")
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

makedir(f"plots/{args.ld_panel}")
plt.savefig(f"plots/{args.ld_panel}/simulation_h2_estimation.pdf")
plt.close()

plt.figure(figsize=(9, 6))
g = sns.catplot(x="Prop. Causal", y="Estimated Prop. Causal",
                hue="Model", col="Heritability",
                data=final_df, kind="box")
plt.savefig(f"plots/{args.ld_panel}/simulation_pi_estimation.pdf", bbox_inches='tight')

