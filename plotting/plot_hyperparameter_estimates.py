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

dfs = []

for f in glob.glob("data/model_fit/*/*/*/chr_22.hyp"):

    df = pd.read_csv(f, index_col=0).T
    df.columns = ['Estimated ' + c for c in df.columns]

    _, _, model, config, trait, _ = f.split("/")
    df['Trait'] = trait
    _, h2, _, p = config.split("_")
    df['Heritability'] = float(h2)
    df['Prop. Causal'] = float(p)
    df['Model'] = model

    dfs.append(df)

final_df = pd.concat(dfs)

g = sns.catplot(x="Heritability", y="Estimated Heritability",
                hue="Model", col="Prop. Causal",
                data=final_df, kind="box")

makedir("plots/")
plt.savefig("plots/simulation_h2_estimation.pdf")
plt.close()

g = sns.catplot(x="Prop. Causal", y="Estimated Prop. Causal",
                hue="Model", col="Heritability",
                data=final_df, kind="box")

plt.savefig("plots/simulation_pi_estimation.pdf")

