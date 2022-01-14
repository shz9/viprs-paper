import os.path as osp
import sys
sys.path.append(osp.dirname(osp.dirname(__file__)))
from utils import makedir
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import functools
import argparse
from plot_utils import *
print = functools.partial(print, flush=True)

# -------------------- Helper functions --------------------


def extract_time_stats(phenotype_type=None,
                       configuration=None,
                       keep_models=None,
                       keep_panels=None,
                       keep_traits=None,
                       exclude_nan=False):
    """
    Extract time statistics from log files and combine them for plotting
    :param phenotype_type: Can be `quantitative`, `binary`, or None (both)
    :param configuration: Can be `real`, `simulation`, or None (both)
    :param keep_models: Only keep a subset of the models
    :param keep_panels: The LD reference panel to use
    :param keep_traits: Extract data for only a subset of traits.
    :param exclude_nan: Exclude statistics where time is not reported properly.
    """

    if phenotype_type is None:
        phenotype_type = '*'

    if configuration is None:
        configuration = '*'
    elif configuration == 'simulation':
        configuration = 'h2_*'
    elif configuration == 'real':
        configuration = 'real_fold_*'

    time_stats = []

    # Loop over the log files and extract the duration for each run
    # as well as associated info (e.g. configuration, model, LD panel, etc.):
    for log_f in glob.glob(f"log/model_fit/*/*/{phenotype_type}/{configuration}/*.out"):

        _, _, panel, model, trait_type, config, trait = log_f.split('/')

        if keep_models is not None:
            if model not in keep_models:
                continue

        if keep_panels is not None:
            if panel not in keep_panels:
                continue

        if keep_traits is not None:
            if trait not in keep_traits:
                continue

        trait = trait.replace('.out', '')
        if 'real' in config:
            config = config.split('_')[0]

        try:
            with open(log_f, 'r') as f:
                lines = f.read().splitlines()
                duration = float(lines[-1].split(':')[-1].strip())

        except Exception as e:
            print("Error parsing the log file:", log_f)
            print("Error message:", e)
            duration = np.nan

        if exclude_nan and np.isnan(duration):
            print("Skipping...")
            continue

        time_stats.append({'LD Panel': panel,
                           'Configuration': config,
                           'Class': ['Quantitative', 'Binary'][trait_type == 'binary'],
                           'Trait': trait,
                           'Model': model,
                           'Duration_minutes': duration})

    # Concatenate the entries into a single dataframe:
    return pd.DataFrame(time_stats)


def plot_time_stats(time_stats_df,
                    units='hours',
                    x_label_rotation=90,
                    model_order=None,
                    showfliers=False,
                    palette='Set2',
                    ax=None):

    assert units in ('hours', 'minutes', 'log_minutes')

    if units == 'hours':
        time_stats_df['Duration_hours'] = time_stats_df['Duration_minutes'] / 60
    elif units == 'log_minutes':
        time_stats_df['Duration_log_minutes'] = np.log(time_stats_df['Duration_minutes'])

    g = sns.boxplot(x="Model", y="Duration_" + units,
                    data=time_stats_df,
                    showfliers=showfliers,
                    palette=palette,
                    order=model_order,
                    ax=ax)

    if x_label_rotation != 0:
        g.set_xticklabels(g.get_xticklabels(), rotation=x_label_rotation)

    if units == 'hours':
        plt.ylabel("Model Runtime (Hours)")
    elif units == 'minutes':
        plt.ylabel("Model Runtime (Minutes)")
    elif units == 'log_minutes':
        plt.ylabel("Model Runtime (Log Minutes)")

    return g

# -----------------------------------------------------------------

def main():

    parser = argparse.ArgumentParser(description='Plot time statistics for PRS models')
    parser.add_argument('-m', '--models', dest='models', type=str)
    parser.add_argument('--prefix', dest='prefix', type=str)
    parser.add_argument('--extension', dest='ext', type=str, default='eps')
    args = parser.parse_args()

    print("> Plotting time statistics for PRS methods...")

    # Extract data:
    time_df = extract_time_stats()

    # Update model names:
    time_df = update_model_names(time_df)

    sns.set_style("darkgrid")
    sns.set_context("paper")

    # ---------------------------------------------------------
    # Plot 1: Plot time statistics for simulations by LD panel:

    print("> Plotting time statistics by LD panel for simulations...")

    ldp_time_df = time_df.loc[time_df['Configuration'] != 'real']

    for ldp in ldp_time_df['LD Panel'].unique():

        if ldp == 'external':
            continue

        df = ldp_time_df.loc[ldp_time_df['LD Panel'].isin(['external', ldp])]

        plt.figure(figsize=(7, 4))
        plot_time_stats(df, model_order=sort_models(df['Model'].unique()))

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

    ldp_time_df = time_df.loc[time_df['Configuration'] == 'real']

    for ldp in ldp_time_df['LD Panel'].unique():

        if ldp == 'external':
            continue

        df = ldp_time_df.loc[ldp_time_df['LD Panel'].isin(['external', ldp])]

        plt.figure(figsize=(7, 4))
        plot_time_stats(df, model_order=sort_models(df['Model'].unique()))

        if args.prefix is None:
            final_output_dir = f"plots/runtime_stats/{ldp}"
        else:
            final_output_dir = f"plots/runtime_stats/{ldp}/{args.prefix}"

        makedir(final_output_dir)
        plt.savefig(osp.join(final_output_dir, "real." + args.ext), bbox_inches='tight')
        plt.close()


if __name__ == '__main__':
    main()
