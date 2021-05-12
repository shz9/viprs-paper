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

for f in glob.glob("data/evaluation/*/*.csv"):
    df = pd.read_csv(f)
    config = osp.basename(osp.dirname(f))
    _, h2, _, p = config.split("_")
    df['Heritability'] = float(h2)
    df['Prop. Causal'] = float(p)

    dfs.append(df)

final_df = pd.concat(dfs)

g = sns.catplot(x="Heritability", y="R2",
                hue="Model", col="Prop. Causal",
                data=final_df, kind="box")

makedir("plots/")
plt.savefig("plots/simulation_predictive_performance.pdf")
