"""
This script generates plots for the third figure in the manuscript
where we show the aggregated runtime of each PRS model.
"""

from plot_time_stats import *

parser = argparse.ArgumentParser(description='Generate Figure 3')
parser.add_argument('--extension', dest='ext', type=str, default='eps')
args = parser.parse_args()

# Extract data:
keep_models = ['VIPRS', 'VIPRS-GSv_p', 'SBayesR', 'Lassosum', 'LDPred2-grid', 'PRScs', 'PRSice2']
keep_traits = ['HEIGHT', 'HDL', 'BMI', 'FVC', 'FEV1', 'HC', 'WC', 'LDL', 'BW', 'ASTHMA', 'T2D', 'RA']

sim_time_stats = extract_time_stats(keep_models=keep_models,
                                    configuration='simulation',
                                    keep_panels=['ukbb_50k_windowed', 'external'])
sim_time_stats = update_model_names(sim_time_stats)

real_time_stats = extract_time_stats(keep_models=keep_models,
                                     configuration='real',
                                     keep_panels=['ukbb_50k_windowed', 'external'],
                                     keep_traits=keep_traits)
real_time_stats = update_model_names(real_time_stats)

# Set seaborn context:
makedir("plots/main_figures/figure_3/")
sns.set_style("darkgrid")
sns.set_context("paper")


# Generate a combined figure:
plt.figure(figsize=set_figure_size(width='paper'))

combined_tstats_df = pd.concat([sim_time_stats, real_time_stats])

plot_time_stats(combined_tstats_df, units='hours',
                model_order=sort_models(combined_tstats_df['Model'].unique()))

plt.savefig("plots/main_figures/figure_3/3." + args.ext, bbox_inches='tight')
plt.close()

# Generate separated figures (sanity checking only):

plt.figure(figsize=set_figure_size(width='paper'))

plot_time_stats(sim_time_stats, units='hours',
                model_order=sort_models(sim_time_stats['Model'].unique()))

plt.savefig("plots/main_figures/figure_3/3_sim." + args.ext, bbox_inches='tight')
plt.close()

plt.figure(figsize=set_figure_size(width='paper'))

plot_time_stats(real_time_stats, units='hours',
                model_order=sort_models(real_time_stats['Model'].unique()))

plt.savefig("plots/main_figures/figure_3/3_real." + args.ext, bbox_inches='tight')
plt.close()
