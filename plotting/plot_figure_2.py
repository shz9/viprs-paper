"""
This script generates plots for the second figure in the manuscript
where we show predictive performance on real quantitative
and binary (case/control) phenotypes.
"""

from plot_predictive_performance import *

parser = argparse.ArgumentParser(description='Generate Figure 1')
parser.add_argument('--extension', dest='ext', type=str, default='eps')
args = parser.parse_args()

# Extract data:
keep_models = ['VIPRS', 'VIPRS-GSv_p', 'SBayesR', 'Lassosum', 'LDPred2-grid', 'PRScs', 'PRSice2']

bin_real_data = extract_predictive_evaluation_data(phenotype_type='binary',
                                                   configuration='real',
                                                   keep_models=keep_models,
                                                   keep_panels=['ukbb_50k_windowed', 'external'],
                                                   keep_traits=['ASTHMA', 'T2D', 'RA'])
bin_real_data = update_model_names(bin_real_data)

quant_real_data = extract_predictive_evaluation_data(phenotype_type='quantitative',
                                                    configuration='real',
                                                    keep_models=keep_models,
                                                    keep_panels=['ukbb_50k_windowed', 'external'])
quant_real_data = update_model_names(quant_real_data)


# Set seaborn context:
sns.set_style("darkgrid")
sns.set_context("paper")

# Create plot:

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=set_figure_size('paper', subplots=(1, 2)))

plot_real_predictive_performance(quant_real_data,
                                 model_order=sort_models(quant_real_data['Model'].unique()),
                                 row_order=sort_traits('quantitative', quant_real_data['Trait'].unique()),
                                 col_order=sort_traits('quantitative', quant_real_data['Trait'].unique()),
                                 col_wrap=3,
                                 ax=ax1)
plot_real_predictive_performance(bin_real_data,
                                 metric='ROC-AUC',
                                 row_order=sort_traits('binary', bin_real_data['Trait'].unique()),
                                 model_order=sort_models(bin_real_data['Model'].unique()),
                                 col_wrap=1,
                                 ax=ax2)

makedir("plots/main_figures")
plt.savefig("plots/main_figures/figure_2." + args.ext, bbox_inches='tight')
plt.close()
