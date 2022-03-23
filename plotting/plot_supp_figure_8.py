"""
This script generates plots for the eighth supplementary figure in the manuscript
where we show hyperparameter estimates for quantitative
and binary (case/control) phenotypes.
"""

from plot_hyperparameter_estimates import *

parser = argparse.ArgumentParser(description='Generate Supplementary Figure 8')
parser.add_argument('--extension', dest='ext', type=str, default='eps')
args = parser.parse_args()

# Extract data:
keep_models = ['VIPRS', 'VIPRS-GSv_p', 'VIPRS-GS_p', 'VIPRS-BO_p', 'VIPRS-BOv_p', 'SBayesR']
keep_panels = ['ukbb_50k_windowed', 'external']

bin_real_data = extract_hyperparameter_estimates_data(phenotype_type='binary',
                                                      configuration='real',
                                                      keep_models=keep_models,
                                                      keep_panels=keep_panels,
                                                      keep_traits=['ASTHMA', 'T2D', 'PASS_T2D', 'RA', 'PASS_RA'])
bin_real_data = update_model_names(bin_real_data)

quant_real_data = extract_hyperparameter_estimates_data(phenotype_type='quantitative',
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

# --------------------------------------------------------
# Add LDSC heritability estimates from the Heritability Browser (Ben Neale's lab):
# https://nealelab.github.io/UKBB_ldsc/h2_browser.html

ldsc_bin_data = pd.DataFrame({
    'Trait': ['ASTHMA', 'T2D', 'PASS_T2D', 'RA', 'PASS_RA'],
    'Model': ['S-LDSC', 'S-LDSC', 'S-LDSC', 'S-LDSC', 'S-LDSC'],
    'Estimated Heritability': [0.170, 0.14, 0.14, 0.07, 0.07],
    'Estimated Prop. Causal': [np.nan, np.nan, np.nan, np.nan, np.nan],
    'Heritability': [np.nan, np.nan, np.nan, np.nan, np.nan],
    'Prop. Causal': [np.nan, np.nan, np.nan, np.nan, np.nan]
})

bin_real_data = pd.concat([bin_real_data, ldsc_bin_data])

ldsc_quant_data = pd.DataFrame({
    'Trait': ['HEIGHT', 'PASS_HEIGHT', 'HDL', 'PASS_HDL', 'BMI', 'PASS_BMI', 'FVC',
              'FEV1', 'HC', 'WC', 'LDL', 'PASS_LDL', 'BW'],
    'Model': ['S-LDSC', 'S-LDSC', 'S-LDSC', 'S-LDSC', 'S-LDSC', 'S-LDSC', 'S-LDSC', 'S-LDSC', 'S-LDSC',
              'S-LDSC', 'S-LDSC', 'S-LDSC', 'S-LDSC'],
    'Estimated Heritability': [0.485, 0.485, 0.33, 0.33, 0.248, 0.248, 0.21, 0.192, 0.223, 0.206, 0.0825, 0.0825, 0.122],
    'Estimated Prop. Causal': [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan,
                               np.nan, np.nan, np.nan, np.nan],
    'Heritability': [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan,
                     np.nan, np.nan, np.nan, np.nan],
    'Prop. Causal': [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan,
                     np.nan, np.nan, np.nan, np.nan]
})

quant_real_data = pd.concat([quant_real_data, ldsc_quant_data])

# --------------------------------------------------------

# Set seaborn context:
makedir("plots/supplementary_figures/figure_8/")
sns.set_style("darkgrid")
sns.set_context("paper", font_scale=1.8)

# Create plot:

plt.figure(figsize=set_figure_size(width='paper', subplots=(3, 5)))

plot_real_hyperparameter_estimates(quant_real_data,
                                   metric='Estimated Heritability',
                                   model_order=sort_models(quant_real_data['Model'].unique()) + ['S-LDSC'],
                                   row_order=sort_traits('quantitative', quant_real_data['Trait'].unique()),
                                   col_order=sort_traits('quantitative', quant_real_data['Trait'].unique()),
                                   col_wrap=5)
plt.subplots_adjust(wspace=.1)
plt.savefig("plots/supplementary_figures/figure_8/8_a." + args.ext, bbox_inches='tight')
plt.close()

plt.figure(figsize=set_figure_size(width='paper', subplots=(1, 5)))

plot_real_hyperparameter_estimates(bin_real_data,
                                   metric='Estimated Heritability',
                                   model_order=sort_models(bin_real_data['Model'].unique()) + ['S-LDSC'],
                                   row_order=sort_traits('binary', bin_real_data['Trait'].unique()),
                                   col_wrap=5)
plt.subplots_adjust(wspace=.1)
plt.savefig("plots/supplementary_figures/figure_8/8_b." + args.ext, bbox_inches='tight')
plt.close()
