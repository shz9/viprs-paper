import pandas as pd
import sys
import os.path as osp

snp_effects_file = sys.argv[1] + ".snpRes"
hyperparams_file = sys.argv[1] + ".parRes"
sumstats_file = sys.argv[2].replace('.ma', '.PHENO1.glm.linear')

# Read the SNP effects file:
snp_effect_df = pd.read_csv(snp_effects_file, sep="\s+")
snp_effect_df = snp_effect_df[['Chrom', 'Name', 'PIP', 'A1Effect']]
snp_effect_df.columns = ['CHR', 'SNP', 'PIP', 'BETA']

# Read the summary statistics table:
ss_table = pd.read_csv(sumstats_file, sep="\s+")[['CHR', 'SNP', 'A1', 'A2']]

# Merge the summary statistics table with the output table:
snp_effect_df = snp_effect_df.merge(ss_table, how='right')
snp_effect_df.fillna(0., inplace=True)

snp_effect_df = snp_effect_df[['CHR', 'SNP', 'A1', 'A2', 'PIP', 'BETA']]
snp_effect_df.to_csv(snp_effects_file.replace('.snpRes', '.fit'), sep="\t", index=False)

# --------------------------------------------- #
# Transform the hyperparameter estimates:

params = pd.read_csv(hyperparams_file, sep="\s+", skiprows=1)
heritability = params.loc['hsq', 'Mean']
prop_causal = snp_effect_df['PIP'].mean()

hyp_df = pd.DataFrame.from_dict({
        'Heritability': heritability,
        'Prop. Causal': prop_causal
    }, orient='index')

hyp_df.to_csv(hyperparams_file.replace('.parRes', '.hyp'))

