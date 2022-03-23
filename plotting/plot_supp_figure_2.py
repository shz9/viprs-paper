"""
This script generates plots for the second supplementary figure in the manuscript
where we show predictive performance on real quantitative
and binary (case/control) phenotypes.
"""

from plot_predictive_performance import *

parser = argparse.ArgumentParser(description='Generate Supplementary Figure 2')
parser.add_argument('--extension', dest='ext', type=str, default='eps')
args = parser.parse_args()

# Extract data:
keep_models = ['VIPRS']
keep_panels = ['ukbb_1k_shrinkage', 'ukbb_10k_shrinkage', 'ukbb_50k_shrinkage',
               'ukbb_1k_block', 'ukbb_10k_block', 'ukbb_50k_block',
               'ukbb_1k_windowed', 'ukbb_10k_windowed', 'ukbb_50k_windowed']

bin_real_data = extract_predictive_evaluation_data(phenotype_type='binary',
                                                   configuration='real',
                                                   keep_models=keep_models,
                                                   keep_panels=keep_panels,
                                                   keep_traits=['ASTHMA', 'T2D', 'PASS_T2D', 'RA', 'PASS_RA'])
bin_real_data['Model'] = bin_real_data['Model'] + ' (' + bin_real_data['LD Panel'].str.replace('ukbb_', '') + ')'

quant_real_data = extract_predictive_evaluation_data(phenotype_type='quantitative',
                                                     configuration='real',
                                                     keep_models=keep_models,
                                                     keep_panels=keep_panels,
                                                     keep_traits=['HEIGHT', 'PASS_HEIGHT',
                                                                  'HDL', 'PASS_HDL',
                                                                  'BMI', 'PASS_BMI',
                                                                  'FVC', 'FEV1', 'HC',
                                                                  'WC', 'LDL', 'PASS_LDL', 'BW'])
quant_real_data['Model'] = quant_real_data['Model'] + ' (' + quant_real_data['LD Panel'].str.replace('ukbb_', '') + ')'


# Set seaborn context:
makedir("plots/supplementary_figures/figure_2/")
sns.set_style("darkgrid")
sns.set_context("paper", font_scale=1.8)

# Create plot:

plt.figure(figsize=set_figure_size(width='paper', subplots=(3, 5)))

plot_real_predictive_performance(quant_real_data,
                                 model_order=['VIPRS (' + ldp.replace('ukbb_', '') + ')' for ldp in keep_panels],
                                 row_order=sort_traits('quantitative', quant_real_data['Trait'].unique()),
                                 col_order=sort_traits('quantitative', quant_real_data['Trait'].unique()),
                                 col_wrap=5)
plt.subplots_adjust(wspace=.1)
plt.savefig("plots/supplementary_figures/figure_2/2_a." + args.ext, bbox_inches='tight')
plt.close()

plt.figure(figsize=set_figure_size(width='paper', subplots=(1, 5)))

plot_real_predictive_performance(bin_real_data,
                                 metric='PR-AUC',
                                 model_order=['VIPRS (' + ldp.replace('ukbb_', '') + ')' for ldp in keep_panels],
                                 row_order=sort_traits('quantitative', bin_real_data['Trait'].unique()),
                                 col_wrap=5)
plt.subplots_adjust(wspace=.1)
plt.savefig("plots/supplementary_figures/figure_2/2_b." + args.ext, bbox_inches='tight')
plt.close()
