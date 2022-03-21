"""
This script generates plots for the seventh supplementary figure in the manuscript
where we show hyperparameter estimates on simulations for quantitative
and binary (case/control) phenotypes.
"""

from plot_hyperparameter_estimates import *

parser = argparse.ArgumentParser(description='Generate Supplementary Figure 7')
parser.add_argument('--extension', dest='ext', type=str, default='eps')
args = parser.parse_args()

# Extract data:
keep_models = ['VIPRS', 'VIPRS-GSv_p', 'VIPRS-GS_p', 'VIPRS-BO_p', 'VIPRS_BOv_p', 'SBayesR']
keep_panels = ['ukbb_50k_windowed', 'external']

bin_sim_data = extract_hyperparameter_estimates_data(phenotype_type='binary',
                                                     configuration='simulation',
                                                     keep_models=keep_models,
                                                     keep_panels=keep_panels)
bin_sim_data = update_model_names(bin_sim_data)

quant_sim_data = extract_hyperparameter_estimates_data(phenotype_type='quantitative',
                                                       configuration='simulation',
                                                       keep_models=keep_models,
                                                       keep_panels=keep_panels)
quant_sim_data = update_model_names(quant_sim_data)


# Set seaborn context:
sns.set_style("darkgrid")
sns.set_context("paper", font_scale=1.5)

makedir("plots/supplementary_figures/figure_7/")

# Create plot:

# Plot panel (a) for the quantitative phenotypes:
plt.figure(figsize=set_figure_size('paper', subplots=(1, 3)))

plot_simulation_hyperparameter_estimates(quant_sim_data,
                                         metric='Estimated Heritability',
                                         model_order=sort_models(quant_sim_data['Model'].unique()))

plt.savefig("plots/supplementary_figures/figure_7/7_a." + args.ext, bbox_inches='tight')
plt.close()

# Plot panel (b) for the case/control phenotypes:

plt.figure(figsize=set_figure_size('paper', subplots=(1, 3)))

plot_simulation_hyperparameter_estimates(bin_sim_data,
                                         metric='Estimated Heritability',
                                         model_order=sort_models(bin_sim_data['Model'].unique()))
plt.savefig("plots/supplementary_figures/figure_7/7_b." + args.ext, bbox_inches='tight')
plt.close()
