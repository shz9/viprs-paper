"""
This script generates plots for the thirteenth supplementary figure in the manuscript
where we show relative predictive performance in minority populations.
"""

from plot_predictive_performance import *


def plot_relative_predictive_performance(r_df,
                                         metric='R2',
                                         model_order=None,
                                         ancestry_order=None,
                                         palette='Set2'):

    ax = sns.barplot(x="Ancestry",
                     y=metric,
                     hue="Model",
                     data=r_df,
                     hue_order=model_order,
                     order=ancestry_order,
                     palette=palette)

    ax.set(ylabel=metric_name(metric) + " (Relative to White British)", xlabel='Ancestry')

    return ax


parser = argparse.ArgumentParser(description='Generate Supplementary Figure 13')
parser.add_argument('--extension', dest='ext', type=str, default='eps')
args = parser.parse_args()

keep_models = ['VIPRS', 'VIPRS-GSv_p', 'SBayesR', 'Lassosum', 'LDPred2-grid', 'PRScs', 'PRSice2']
keep_panels = ['ukbb_50k_windowed', 'external']

# Extract evaluation data for the White British cohort:

bin_real_data_wb = extract_predictive_evaluation_data(phenotype_type='binary',
                                                      configuration='real',
                                                      keep_models=keep_models,
                                                      keep_panels=keep_panels,
                                                      keep_traits=['ASTHMA', 'T2D', 'RA'])
bin_real_data_wb = update_model_names(bin_real_data_wb)

quant_real_data_wb = extract_predictive_evaluation_data(phenotype_type='quantitative',
                                                        configuration='real',
                                                        keep_models=keep_models,
                                                        keep_panels=keep_panels,
                                                        keep_traits=['HEIGHT', 'HDL', 'BMI',
                                                                     'FVC', 'FEV1', 'HC',
                                                                     'WC', 'LDL', 'BW'])
quant_real_data_wb = update_model_names(quant_real_data_wb)

# Extract data for the minority populations and merge with the corresponding data
# for the White British cohort:

bin_real_data_mp = extract_predictive_evaluation_data(phenotype_type='binary',
                                                      configuration='real',
                                                      keep_models=keep_models,
                                                      keep_panels=keep_panels,
                                                      keep_traits=['ASTHMA', 'T2D', 'RA'],
                                                      eval_dir="data/evaluation_minority")
bin_real_data_mp = update_model_names(bin_real_data_mp)

bin_real_data_combined = bin_real_data_mp.merge(bin_real_data_wb, on=['Trait', 'LD Panel', 'Model', 'Class', 'Fold'])
bin_real_data_combined['PR-AUC'] = bin_real_data_combined['PR-AUC_x'] / bin_real_data_combined['PR-AUC_y']

quant_real_data_mp = extract_predictive_evaluation_data(phenotype_type='quantitative',
                                                        configuration='real',
                                                        keep_models=keep_models,
                                                        keep_panels=keep_panels,
                                                        keep_traits=['HEIGHT', 'HDL', 'BMI',
                                                                     'FVC', 'FEV1', 'HC',
                                                                     'WC', 'LDL', 'BW'],
                                                        eval_dir="data/evaluation_minority")
quant_real_data_mp = update_model_names(quant_real_data_mp)

quant_real_data_combined = quant_real_data_mp.merge(quant_real_data_wb,
                                                    on=['Trait', 'LD Panel', 'Model', 'Class', 'Fold'])
quant_real_data_combined['R2'] = quant_real_data_combined['R2_x'] / quant_real_data_combined['R2_y']

# Plot the data:

# Set seaborn context:
makedir("plots/supplementary_figures/figure_13/")
sns.set_style("darkgrid")
sns.set_context("paper", font_scale=1.2)

# Create plot:

plt.figure(figsize=set_figure_size(width='paper'))
plot_relative_predictive_performance(quant_real_data_combined, metric='R2',
                                     model_order=['VIPRS', 'VIPRS-GS', 'SBayesR',
                                                  'Lassosum', 'LDPred2-grid', 'PRScs', 'PRSice2'],
                                     ancestry_order=['Italy', 'India', 'China', 'Nigeria'])
plt.savefig("plots/supplementary_figures/figure_13/13_a." + args.ext, bbox_inches='tight')
plt.close()

plt.figure(figsize=set_figure_size(width='paper'))
plot_relative_predictive_performance(bin_real_data_combined, metric='PR-AUC',
                                     model_order=['VIPRS', 'VIPRS-GS', 'SBayesR',
                                                  'Lassosum', 'LDPred2-grid', 'PRScs', 'PRSice2'],
                                     ancestry_order=['Italy', 'India', 'China', 'Nigeria'])
plt.savefig("plots/supplementary_figures/figure_13/13_b." + args.ext, bbox_inches='tight')
plt.close()

