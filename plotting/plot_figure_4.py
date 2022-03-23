"""
This script generates plots for the fourth figure in the manuscript
where we show predictive performance on real quantitative
and binary (case/control) phenotypes.
"""

from plot_predictive_performance import *

parser = argparse.ArgumentParser(description='Generate Figure 4')
parser.add_argument('--extension', dest='ext', type=str, default='eps')
args = parser.parse_args()


# Extract data:
keep_models = ['VIPRS', 'VIPRSMix', 'VIPRS-GSv_p', 'SBayesR']
keep_panels = ['ukbb_50k_windowed', 'external']

bin_real_data = extract_predictive_evaluation_data(phenotype_type='binary',
                                                   configuration='real',
                                                   keep_models=keep_models,
                                                   keep_panels=keep_panels,
                                                   keep_traits=['ASTHMA', 'T2D', 'RA'])
bin_real_data = update_model_names(bin_real_data)


quant_real_data = extract_predictive_evaluation_data(phenotype_type='quantitative',
                                                     configuration='real',
                                                     keep_models=keep_models,
                                                     keep_panels=keep_panels,
                                                     keep_traits=['HEIGHT', 'HDL', 'BMI',
                                                                  'FVC', 'FEV1', 'HC',
                                                                  'WC', 'LDL', 'BW']
                                                     )
quant_real_data = update_model_names(quant_real_data)


bin_real_10m = extract_predictive_evaluation_data_all(phenotype_type='binary',
                                                      configuration='real',
                                                      keep_models=['VIPRS', 'VIPRSMix'],
                                                      keep_traits=['ASTHMA', 'T2D', 'RA'])
bin_real_10m['Model'] = bin_real_10m['Model'].map({'VIPRS': 'VIPRS-10m',
                                                   'VIPRSMix': 'VIPRSMix-10m'})

bin_real_data = pd.concat([bin_real_data, bin_real_10m])

quant_real_10m = extract_predictive_evaluation_data_all(phenotype_type='quantitative',
                                                        keep_models=['VIPRS', 'VIPRSMix'],
                                                        configuration='real',
                                                        keep_traits=['HEIGHT', 'HDL', 'BMI',
                                                                     'FVC', 'FEV1', 'HC',
                                                                     'WC', 'LDL', 'BW']
                                                        )

quant_real_10m['Model'] = quant_real_10m['Model'].map({'VIPRS': 'VIPRS-10m',
                                                       'VIPRSMix': 'VIPRSMix-10m'})

quant_real_data = pd.concat([quant_real_data, quant_real_10m])

# Set seaborn context:
makedir("plots/main_figures/figure_4/")
sns.set_style("darkgrid")
sns.set_context("paper", font_scale=2.3)

# Create plot:

plt.figure(figsize=set_figure_size(width=.75*505.89, subplots=(3, 3)))

plot_real_predictive_performance(quant_real_data,
                                 model_order=['VIPRS', 'VIPRSMix',
                                              'VIPRS-10m', 'VIPRSMix-10m',
                                              'VIPRS-GS', 'SBayesR'],
                                 row_order=sort_traits('quantitative', quant_real_data['Trait'].unique()),
                                 col_order=sort_traits('quantitative', quant_real_data['Trait'].unique()),
                                 col_wrap=3,
                                 palette=['#b2df8a', '#33a02c', '#a6cee3', '#1f78b4', '#fc8d62', '#cab2d6'])
plt.subplots_adjust(wspace=.1)
plt.savefig("plots/main_figures/figure_4/4_a." + args.ext, bbox_inches='tight')
plt.close()


plt.figure(figsize=set_figure_size(width=.25*505.89, subplots=(3, 1)))

plot_real_predictive_performance(bin_real_data,
                                 metric='PR-AUC',
                                 model_order=['VIPRS', 'VIPRSMix',
                                              'VIPRS-10m', 'VIPRSMix-10m',
                                              'VIPRS-GS', 'SBayesR'],
                                 row_order=sort_traits('binary', bin_real_data['Trait'].unique()),
                                 col_wrap=1,
                                 palette=['#b2df8a', '#33a02c', '#a6cee3', '#1f78b4', '#fc8d62', '#cab2d6'])
plt.subplots_adjust(wspace=.1)
plt.savefig("plots/main_figures/figure_4/4_b." + args.ext, bbox_inches='tight')
plt.close()

