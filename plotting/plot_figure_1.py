"""
This script generates plots for the first figure in the manuscript
where we show predictive performance on simulations for quantitative
and binary (case/control) phenotypes.
"""

from plot_predictive_performance import *

parser = argparse.ArgumentParser(description='Generate Figure 1')
parser.add_argument('--extension', dest='ext', type=str, default='eps')
args = parser.parse_args()

# Extract data:
keep_models = ['VIPRS', 'VIPRS-GSv_p', 'SBayesR', 'Lassosum', 'LDPred2-grid', 'PRScs', 'PRSice2']

bin_sim_data = extract_predictive_evaluation_data(phenotype_type='binary',
                                                  configuration='simulation',
                                                  keep_models=keep_models,
                                                  keep_panels=['ukbb_50k_windowed', 'external'])
bin_sim_data = update_model_names(bin_sim_data)

quant_sim_data = extract_predictive_evaluation_data(phenotype_type='quantitative',
                                                    configuration='simulation',
                                                    keep_models=keep_models,
                                                    keep_panels=['ukbb_50k_windowed', 'external'])
quant_sim_data = update_model_names(quant_sim_data)


# Set seaborn context:
sns.set_style("darkgrid")
sns.set_context("paper", font_scale=2)

makedir("plots/main_figures/figure_1/")

# Create plot:

# Plot panel (a) for the quantitative phenotypes:
plt.figure(figsize=set_figure_size('paper', subplots=(1, 3)))

plot_simulation_predictive_performance(quant_sim_data,
                                       model_order=sort_models(quant_sim_data['Model'].unique()))

plt.savefig("plots/main_figures/figure_1/1_a." + args.ext, bbox_inches='tight')
plt.close()

# Plot panel (b) for the case/control phenotypes:

plt.figure(figsize=set_figure_size('paper', subplots=(1, 3)))

plot_simulation_predictive_performance(bin_sim_data,
                                       metric='PR-AUC',
                                       model_order=sort_models(bin_sim_data['Model'].unique()))
plt.savefig("plots/main_figures/figure_1/1_b." + args.ext, bbox_inches='tight')
plt.close()
