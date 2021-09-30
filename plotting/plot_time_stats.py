import os.path as osp
import sys
sys.path.append(osp.dirname(osp.dirname(__file__)))
from utils import makedir
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import functools
import argparse
from plot_utils import update_model_names
print = functools.partial(print, flush=True)


parser = argparse.ArgumentParser(description='Plot time statistics for PRS models')
parser.add_argument('-m', '--models', dest='models', type=str)
parser.add_argument('--prefix', dest='prefix', type=str)
parser.add_argument('--extension', dest='ext', type=str, default='eps')
args = parser.parse_args()

print("> Plotting time statistics for PRS methods...")

order = [
    'VIPRS',
    'VIPRSSBayes',
    'VIPRS-GS', 'VIPRS-GSv', 'VIPRS-GSl', 'VIPRS-GSvl',
    'VIPRS-BO', 'VIPRS-BOv',
    'VIPRS-BMA',
    'SBayesR',
    'Lassosum',
    'LDPred2-inf', 'LDPred2-auto', 'LDPred2-grid',
    'PRScs',
    'PRSice2',
]

time_df = []

# Loop over the log files and extract the duration for each run
# as well as associated info (e.g. configuration, model, LD panel, etc.):
for log_f in glob.glob("log/model_fit/*/*/*/*.out"):

    _, _, panel, model, config, trait = log_f.split('/')

    if args.models is not None:
        if model not in args.models.split(","):
            continue

    trait = trait.replace('.out', '')
    if 'real' in config:
        config = config.split('_')[0]

    try:
        with open(log_f, 'r') as f:
            lines = f.read().splitlines()
            duration = float(lines[-1].split(':')[-1].strip())

        time_df.append({'LD Panel': panel,
                        'Configuration': config,
                        'Trait': trait,
                        'Model': model,
                        'Duration': duration / 60})

    except Exception as e:
        print("Error parsing the log file:", log_f)
        print("Error message:", e)
        print("Skipping...")
        continue

# Concatenate the entries into a single dataframe:
time_df = pd.DataFrame(time_df)

# Update model names:
time_df = update_model_names(time_df)

sns.set_style("darkgrid")
sns.set_context("paper")

# ---------------------------------------------------------
# Plot 1: Plot time statistics for simulations by LD panel:

print("> Plotting time statistics by LD panel for simulations...")

ldp_time_df = time_df.loc[time_df['Configuration'] != 'real'].groupby(
    ['LD Panel', 'Configuration', 'Trait', 'Model']
).sum().reset_index()

for ldp in ldp_time_df['LD Panel'].unique():

    if ldp == 'external':
        continue

    df = ldp_time_df.loc[ldp_time_df['LD Panel'].isin(['external', ldp])]

    plt.figure(figsize=(7, 4))
    ax = sns.boxplot(x="Model", y="Duration", data=df,
                     showfliers=False, palette='Set2', order=[m for m in order if m in df['Model'].unique()])
    ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
    plt.ylabel("Runtime (Hours)")

    if args.prefix is None:
        final_output_dir = f"plots/runtime_stats/{ldp}"
    else:
        final_output_dir = f"plots/runtime_stats/{ldp}/{args.prefix}"

    makedir(final_output_dir)
    plt.savefig(osp.join(final_output_dir, "simulation." + args.ext), bbox_inches='tight')
    plt.close()

# ---------------------------------------------------------
# Plot 2: Plot time statistics for real data by LD panel:

print("> Plotting time statistics by LD panel for real data...")

ldp_time_df = time_df.loc[time_df['Configuration'] == 'real'].groupby(
    ['LD Panel', 'Configuration', 'Trait', 'Model']
).sum().reset_index()

for ldp in ldp_time_df['LD Panel'].unique():

    if ldp == 'external':
        continue

    df = ldp_time_df.loc[ldp_time_df['LD Panel'].isin(['external', ldp])]

    plt.figure(figsize=(7, 4))
    ax = sns.boxplot(x="Model", y="Duration", data=df, showfliers=False,
                     palette='Set2',
                     order=[m for m in order if m in df['Model'].unique()])
    ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
    plt.ylabel("Runtime (Hours)")

    if args.prefix is None:
        final_output_dir = f"plots/runtime_stats/{ldp}"
    else:
        final_output_dir = f"plots/runtime_stats/{ldp}/{args.prefix}"

    makedir(final_output_dir)
    plt.savefig(osp.join(final_output_dir, "real." + args.ext), bbox_inches='tight')
    plt.close()
