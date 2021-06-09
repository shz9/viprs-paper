import pandas as pd
import sys
import os.path as osp

snp_effects_file = osp.join(sys.argv[1], "chr_22.snpRes")
hyperparams_file = osp.join(sys.argv[1], "chr_22.parRes")

snp_effect_df = pd.read_csv(snp_effects_file, sep="\t")
snp_effect_df = snp_effect_df[['Chrom', 'Name', 'PIP', 'A1Effect']]
snp_effect_df.columns = ['CHR', 'SNP', 'PIP', 'BETA']
snp_effect_df.to_csv(snp_effects_file.replace('.snpRes', '.fit'), sep="\t", index=False)

params = pd.read_csv(hyperparams_file, sep="\s+", skiprows=1)
heritability = params.loc['hsq', 'Mean']
prop_causal = snp_effect_df['PIP'].mean()

hyp_df = pd.DataFrame.from_dict({
        'Heritability': heritability,
        'Prop. Causal': prop_causal
    }, orient='index')

hyp_df.to_csv(hyperparams_file.replace('.parRes', '.hyp'))

