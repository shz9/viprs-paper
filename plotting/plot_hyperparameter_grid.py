import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os.path as osp
import glob
import argparse


parser = argparse.ArgumentParser(description='Plot hyperparameter grid metrics')
parser.add_argument('-m', '--model', dest='model', type=str, default="VIPRS-GSv",
                    choices={'VIPRS-GSv', 'VIPRS-GSvl', 'VIPRS-BOv'})
parser.add_argument('--extension', dest='ext', type=str, default='eps')
args = parser.parse_args()

agg_res = []

for f_name in glob.glob(f"data/model_fit/ukbb_50k_windowed/{args.model}/*/*/*.validation"):

    chr_name = osp.basename(f_name).replace('.validation', '')
    trait = osp.basename(osp.dirname(f_name))
    config = osp.basename(osp.dirname(osp.dirname(f_name)))

    valid_df = pd.read_csv(f_name, sep="\t")
    valid_df['pi'] = np.log10(valid_df['pi']).round(3)
    valid_df['sigma_epsilon'] = valid_df['sigma_epsilon'].round(3)
    valid_df['chromosome'] = chr_name
    valid_df['Trait'] = trait
    valid_df['Config'] = config
    valid_df['Simulation'] = 'real' not in config

    agg_res.append(valid_df)

    sns.heatmap(valid_df.pivot("sigma_epsilon", "pi", "ELBO"))
    plt.xlabel("$log_{10}(\pi)$")
    plt.ylabel("$\sigma_\epsilon^2$")