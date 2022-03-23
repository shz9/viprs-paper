"""
This script generates plots for the first supplementary figure in the manuscript
where we show predictive performance on simulations for quantitative
and binary (case/control) phenotypes.
"""

from plot_predictive_performance import *

parser = argparse.ArgumentParser(description='Generate Supplementary Figure 1')
parser.add_argument('--extension', dest='ext', type=str, default='eps')
args = parser.parse_args()

# Extract data:
keep_models = ['VIPRS']
keep_panels = ['ukbb_1k_shrinkage', 'ukbb_10k_shrinkage', 'ukbb_50k_shrinkage',
               'ukbb_1k_block', 'ukbb_10k_block', 'ukbb_50k_block',
               'ukbb_1k_windowed', 'ukbb_10k_windowed', 'ukbb_50k_windowed']

bin_sim_data = extract_predictive_evaluation_data(phenotype_type='binary',
                                                  configuration='simulation',
                                                  keep_models=keep_models,
                                                  keep_panels=keep_panels)
bin_sim_data['Model'] = bin_sim_data['Model'] + ' (' + bin_sim_data['LD Panel'].str.replace('ukbb_', '') + ')'

quant_sim_data = extract_predictive_evaluation_data(phenotype_type='quantitative',
                                                    configuration='simulation',
                                                    keep_models=keep_models,
                                                    keep_panels=keep_panels)
quant_sim_data['Model'] = quant_sim_data['Model'] + ' (' + quant_sim_data['LD Panel'].str.replace('ukbb_', '') + ')'


# Set seaborn context:
sns.set_style("darkgrid")
sns.set_context("paper", font_scale=1.5)

makedir("plots/supplementary_figures/figure_1/")

# Create plot:

# Plot panel (a) for the quantitative phenotypes:
plt.figure(figsize=set_figure_size('paper', subplots=(1, 3)))

plot_simulation_predictive_performance(quant_sim_data,
                                       model_order=['VIPRS (' + ldp.replace('ukbb_', '') + ')' for ldp in keep_panels])

plt.savefig("plots/supplementary_figures/figure_1/1_a." + args.ext, bbox_inches='tight')
plt.close()

# Plot panel (b) for the case/control phenotypes:

plt.figure(figsize=set_figure_size('paper', subplots=(1, 3)))

plot_simulation_predictive_performance(bin_sim_data,
                                       metric='PR-AUC',
                                       model_order=['VIPRS (' + ldp.replace('ukbb_', '') + ')' for ldp in keep_panels])
plt.savefig("plots/supplementary_figures/figure_1/1_b." + args.ext, bbox_inches='tight')
plt.close()
