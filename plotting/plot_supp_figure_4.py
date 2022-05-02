"""
This script generates plots for the fourth supplementary figure in the manuscript
where we show predictive performance on real quantitative
and binary (case/control) phenotypes.
"""

from plot_predictive_performance import *

parser = argparse.ArgumentParser(description='Generate Supplementary Figure 4')
parser.add_argument('--extension', dest='ext', type=str, default='eps')
args = parser.parse_args()


# Extract data:
keep_models = ['VIPRS', 'VIPRSMix', 'VIPRSAlpha', 'VIPRS-GSv_p', 'VIPRSMix-GSv_p', 'VIPRSAlpha-GSv_p']
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
                                                                  'WC', 'LDL', 'PASS_LDL', 'BW']
                                                     )
quant_real_data = update_model_names(quant_real_data)


bin_real_10m = extract_predictive_evaluation_data(phenotype_type='binary',
                                                  configuration='real',
                                                  keep_models=['VIPRS', 'VIPRSMix', 'VIPRSAlpha'],
                                                  keep_traits=['ASTHMA', 'T2D', 'RA'],
                                                  eval_dir="data_all/evaluation")
bin_real_10m['Model'] = bin_real_10m['Model'].map({'VIPRS': 'VIPRS-10m',
                                                   'VIPRSMix': 'VIPRSMix-10m',
                                                   'VIPRSAlpha': 'VIPRSAlpha-10m'})

bin_real_data = pd.concat([bin_real_data, bin_real_10m])

quant_real_10m = extract_predictive_evaluation_data(phenotype_type='quantitative',
                                                    configuration='real',
                                                    keep_models=['VIPRS', 'VIPRSMix', 'VIPRSAlpha'],
                                                    keep_traits=['HEIGHT', 'HDL', 'BMI',
                                                                 'FVC', 'FEV1', 'HC',
                                                                 'WC', 'LDL', 'BW'],
                                                    eval_dir="data_all/evaluation")

quant_real_10m['Model'] = quant_real_10m['Model'].map({'VIPRS': 'VIPRS-10m',
                                                       'VIPRSMix': 'VIPRSMix-10m',
                                                       'VIPRSAlpha': 'VIPRSAlpha-10m'})

quant_real_data = pd.concat([quant_real_data, quant_real_10m])

# Set seaborn context:
makedir("plots/supplementary_figures/figure_4/")
sns.set_style("darkgrid")
sns.set_context("paper", font_scale=1.9)

# Create plot:

plt.figure(figsize=set_figure_size(width='paper', subplots=(3, 5)))

plot_real_predictive_performance(quant_real_data,
                                 model_order=['VIPRS', 'VIPRSMix', 'VIPRSAlpha',
                                              'VIPRS-10m', 'VIPRSMix-10m', 'VIPRSAlpha-10m',
                                              'VIPRS-GS', 'VIPRSMix-GS', 'VIPRSAlpha-GS'],
                                 row_order=sort_traits('quantitative', quant_real_data['Trait'].unique()),
                                 col_order=sort_traits('quantitative', quant_real_data['Trait'].unique()),
                                 col_wrap=5)
plt.subplots_adjust(wspace=.1)
plt.savefig("plots/supplementary_figures/figure_4/4_a." + args.ext, bbox_inches='tight')
plt.close()


plt.figure(figsize=set_figure_size(width='paper', subplots=(1, 5)))

plot_real_predictive_performance(bin_real_data,
                                 metric='PR-AUC',
                                 model_order=['VIPRS', 'VIPRSMix', 'VIPRSAlpha',
                                              'VIPRS-10m', 'VIPRSMix-10m', 'VIPRSAlpha-10m',
                                              'VIPRS-GS', 'VIPRSMix-GS', 'VIPRSAlpha-GS'],
                                 row_order=sort_traits('binary', bin_real_data['Trait'].unique()),
                                 col_wrap=5)
plt.subplots_adjust(wspace=.1)
plt.savefig("plots/supplementary_figures/figure_4/4_b." + args.ext, bbox_inches='tight')
plt.close()
