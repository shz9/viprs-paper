"""
This script generates plots for the fourth main figure in the manuscript
where we show relative predictive performance in minority populations.
"""

from plot_predictive_performance import *


def plot_relative_predictive_performance(r_df,
                                         metric='R2',
                                         model_order=None,
                                         ancestry_order=None,
                                         trait_order=None,
                                         col_wrap=3,
                                         add_hatches=True,
                                         palette='Set2'):

    g = sns.catplot(x="Ancestry",
                    y=metric,
                    col="Trait",
                    data=r_df,
                    kind="bar",
                    hue="Model",
                    col_wrap=col_wrap,
                    order=ancestry_order,
                    hue_order=model_order,
                    row_order=trait_order,
                    col_order=trait_order,
                    palette=palette)

    if add_hatches:
        add_hatch_to_facet_plot(g, patch_index=np.arange(8))

    for fig_ax in g.fig.axes:
        fig_ax.set_title(fig_ax.get_title().replace("Trait = ", ""))

    g.set_axis_labels("Ancestry group", "Relative " + metric_name(metric))

    return g


parser = argparse.ArgumentParser(description='Generate Figure 4')
parser.add_argument('--extension', dest='ext', type=str, default='eps')
args = parser.parse_args()

keep_models = ['VIPRS', 'VIPRS-GSv_p', 'SBayesR', 'Lassosum', 'MegaPRS', 'LDPred2-grid', 'PRScs', 'PRSice2']
keep_panels = ['ukbb_50k_windowed', 'external']

# Extract evaluation data for the White British cohort:
"""
bin_real_data_wb = extract_predictive_evaluation_data(phenotype_type='binary',
                                                      configuration='real',
                                                      keep_models=keep_models,
                                                      keep_panels=keep_panels,
                                                      keep_traits=['ASTHMA', 'T2D', 'RA'])
bin_real_data_wb = update_model_names(bin_real_data_wb)
"""

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
"""
bin_real_data_mp = extract_predictive_evaluation_data(phenotype_type='binary',
                                                      configuration='real',
                                                      keep_models=keep_models,
                                                      keep_panels=keep_panels,
                                                      keep_traits=['ASTHMA', 'T2D', 'RA'],
                                                      eval_dir="data/evaluation_minority")
bin_real_data_mp = update_model_names(bin_real_data_mp)

max_perf = bin_real_data_wb.groupby(['Trait', 'Class', 'Fold']).max().reset_index()
bin_real_data_combined = bin_real_data_mp.merge(max_perf[['Trait', 'Class', 'Fold', 'PR-AUC']],
                                                on=['Trait', 'Class', 'Fold'])

#bin_real_data_combined = bin_real_data_mp.merge(bin_real_data_wb, on=['Trait', 'LD Panel', 'Model', 'Class', 'Fold'])
bin_real_data_combined['PR-AUC'] = bin_real_data_combined['PR-AUC_x'] / bin_real_data_combined['PR-AUC_y']
"""


quant_real_data_mp = extract_predictive_evaluation_data(phenotype_type='quantitative',
                                                        configuration='real',
                                                        keep_models=keep_models,
                                                        keep_panels=keep_panels,
                                                        keep_traits=['HEIGHT', 'HDL', 'BMI',
                                                                     'FVC', 'FEV1', 'HC',
                                                                     'WC', 'LDL', 'BW'],
                                                        eval_dir="data/evaluation_minority")
quant_real_data_mp = update_model_names(quant_real_data_mp)

#quant_real_data_combined = quant_real_data_mp.merge(quant_real_data_wb,
#                                                    on=['Trait', 'LD Panel', 'Model', 'Class', 'Fold'])

max_perf = quant_real_data_wb.groupby(['Trait', 'Class', 'Fold']).max().reset_index()
quant_real_data_combined = quant_real_data_mp.merge(max_perf[['Trait', 'Class', 'Fold', 'R2']],
                                                    on=['Trait', 'Class', 'Fold'])

quant_real_data_combined['R2'] = quant_real_data_combined['R2_x'] / quant_real_data_combined['R2_y']

# Plot the data:

# Set seaborn context:
makedir("plots/main_figures/figure_4/")
sns.set_style("darkgrid")
sns.set_context("paper", font_scale=2)

# Create plot:

plt.figure(figsize=set_figure_size(width='paper'))
plot_relative_predictive_performance(quant_real_data_combined,
                                     metric='R2',
                                     model_order=['VIPRS', 'VIPRS-GS', 'SBayesR',
                                                  'Lassosum', 'MegaPRS', 'LDPred2-grid', 'PRScs', 'PRSice2'],
                                     ancestry_order=['Italy', 'India', 'China', 'Nigeria'],
                                     trait_order=sort_traits('quantitative',
                                                             quant_real_data_combined['Trait'].unique()))
plt.subplots_adjust(wspace=.1)
plt.savefig("plots/main_figures/figure_4/4." + args.ext, bbox_inches='tight')
plt.close()

"""
plt.figure(figsize=set_figure_size(width='paper'))
plot_relative_predictive_performance(bin_real_data_combined, metric='PR-AUC',
                                     model_order=['VIPRS', 'VIPRS-GS', 'SBayesR',
                                                  'Lassosum', 'LDPred2-grid', 'PRScs', 'PRSice2'],
                                     ancestry_order=['Italy', 'India', 'China', 'Nigeria'],
                                     col_wrap=1,
                                     trait_order=sort_traits('binary',
                                                             bin_real_data_combined['Trait'].unique()))
plt.subplots_adjust(wspace=.1)
plt.savefig("plots/main_figures/figure_4/4_b." + args.ext, bbox_inches='tight')
plt.close()
"""
