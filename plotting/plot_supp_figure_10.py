"""
This script generates plots for the tenth supplementary figure in the manuscript
where we show hyperparameter estimates for quantitative
and binary (case/control) phenotypes.
"""

from plot_hyperparameter_estimates import *

parser = argparse.ArgumentParser(description='Generate Supplementary Figure 10')
parser.add_argument('--extension', dest='ext', type=str, default='eps')
args = parser.parse_args()

# Extract data:
keep_models = ['VIPRS', 'VIPRS-GSv_p', 'SBayesR']
keep_panels = ['ukbb_50k_windowed', 'external']

bin_real_data = extract_hyperparameter_estimates_data(phenotype_type='binary',
                                                      configuration='real',
                                                      keep_models=keep_models,
                                                      keep_panels=keep_panels,
                                                      keep_traits=['ASTHMA', 'T2D', 'RA'])
bin_real_data = update_model_names(bin_real_data)

quant_real_data = extract_hyperparameter_estimates_data(phenotype_type='quantitative',
                                                        configuration='real',
                                                        keep_models=keep_models,
                                                        keep_panels=keep_panels,
                                                        keep_traits=['HEIGHT', 'HDL', 'BMI',
                                                                     'FVC', 'FEV1', 'HC',
                                                                     'WC', 'LDL', 'BW']
                                                        )
quant_real_data = update_model_names(quant_real_data)

# Set seaborn context:
makedir("plots/supplementary_figures/figure_10/")
sns.set_style("darkgrid")
sns.set_context("paper", font_scale=1.8)

# Create plot:

plt.figure(figsize=set_figure_size(width=.75*505.89, subplots=(3, 3)))

plot_real_hyperparameter_estimates(quant_real_data,
                                   metric='Estimated Prop. Causal',
                                   model_order=sort_models(quant_real_data['Model'].unique()),
                                   row_order=sort_traits('quantitative', quant_real_data['Trait'].unique()),
                                   col_order=sort_traits('quantitative', quant_real_data['Trait'].unique()),
                                   col_wrap=3)

plt.savefig("plots/supplementary_figures/figure_10/10_a." + args.ext, bbox_inches='tight')
plt.close()

plt.figure(figsize=set_figure_size(width=.25*505.89, subplots=(3, 1)))

plot_real_hyperparameter_estimates(bin_real_data,
                                   metric='Estimated Prop. Causal',
                                   model_order=sort_models(bin_real_data['Model'].unique()),
                                   row_order=sort_traits('binary', bin_real_data['Trait'].unique()),
                                   col_wrap=1)

plt.savefig("plots/supplementary_figures/figure_10/10_b." + args.ext, bbox_inches='tight')
plt.close()