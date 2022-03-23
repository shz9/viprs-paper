"""
This script generates plots for the second figure in the manuscript
where we show predictive performance on real quantitative
and binary (case/control) phenotypes.
"""

from plot_predictive_performance import *

parser = argparse.ArgumentParser(description='Generate Supplementary Figure 6')
parser.add_argument('--extension', dest='ext', type=str, default='eps')
args = parser.parse_args()

# Extract data:
keep_models = ['VIPRS', 'VIPRS-GSv_p', 'VIPRS-GS_p', 'VIPRS-BO_p', 'VIPRS-BOv_p', 'VIPRS-BMA_p']
keep_panels = ['ukbb_50k_windowed']

bin_real_data = extract_predictive_evaluation_data(phenotype_type='binary',
                                                   configuration='real',
                                                   keep_models=keep_models,
                                                   keep_panels=keep_panels,
                                                   keep_traits=['ASTHMA', 'T2D', 'PASS_T2D', 'RA', 'PASS_RA'])
bin_real_data = update_model_names(bin_real_data)

quant_real_data = extract_predictive_evaluation_data(phenotype_type='quantitative',
                                                     configuration='real',
                                                     keep_models=keep_models,
                                                     keep_panels=keep_panels,
                                                     keep_traits=['HEIGHT', 'PASS_HEIGHT',
                                                                  'HDL', 'PASS_HDL',
                                                                  'BMI', 'PASS_BMI',
                                                                  'FVC', 'FEV1', 'HC',
                                                                  'WC', 'LDL', 'PASS_LDL', 'BW'])
quant_real_data = update_model_names(quant_real_data)


# Set seaborn context:
makedir("plots/supplementary_figures/figure_6/")
sns.set_style("darkgrid")
sns.set_context("paper", font_scale=1.8)

# Create plot:

plt.figure(figsize=set_figure_size(width='paper', subplots=(3, 5)))

plot_real_predictive_performance(quant_real_data,
                                 model_order=sort_models(quant_real_data['Model'].unique()),
                                 row_order=sort_traits('quantitative', quant_real_data['Trait'].unique()),
                                 col_order=sort_traits('quantitative', quant_real_data['Trait'].unique()),
                                 col_wrap=5)
plt.subplots_adjust(wspace=.1)
plt.savefig("plots/supplementary_figures/figure_6/6_a." + args.ext, bbox_inches='tight')
plt.close()

plt.figure(figsize=set_figure_size(width='paper', subplots=(1, 5)))

plot_real_predictive_performance(bin_real_data,
                                 metric='PR-AUC',
                                 model_order=sort_models(bin_real_data['Model'].unique()),
                                 row_order=sort_traits('binary', bin_real_data['Trait'].unique()),
                                 col_wrap=5)
plt.subplots_adjust(wspace=.1)
plt.savefig("plots/supplementary_figures/figure_6/6_b." + args.ext, bbox_inches='tight')
plt.close()
