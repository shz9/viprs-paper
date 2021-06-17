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

parser = argparse.ArgumentParser(description='Plot predictive performance')
parser.add_argument('-l', '--ld-panel', dest='ld_panel', type=str, default='ukbb_50k_windowed')
args = parser.parse_args()


dfs = []

for f in glob.glob(f"data/evaluation/{args.ld_panel}/*/*.csv") + glob.glob(f"data/evaluation/external/*/*.csv"):
    df = pd.read_csv(f)
    config = osp.basename(osp.dirname(f))
    _, h2, _, p = config.split("_")
    df['Heritability'] = float(h2)
    df['Prop. Causal'] = float(p)

    dfs.append(df)

final_df = pd.concat(dfs)

plt.figure(figsize=(9, 6))
g = sns.catplot(x="Heritability", y="R2",
                hue="Model", col="Prop. Causal",
                data=final_df, kind="box")
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

plt.tight_layout()
makedir(f"plots/{args.ld_panel}")
plt.savefig(f"plots/{args.ld_panel}/simulation_predictive_performance.pdf")
