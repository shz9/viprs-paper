import pandas as pd
import numpy as np
import argparse
import os.path as osp

parser = argparse.ArgumentParser(description='Transform output of SBayesR')

parser.add_argument('-o', '--output', dest='output_dir', type=str, required=True,
                    help='The directory where the SBayesR output files reside')
parser.add_argument('-s', '--sumstats', dest='ss_dir', type=str, required=True,
                    help='The summary statistics files')
parser.add_argument('-t', '--type', dest='type', type=str, default='plink',
                    choices={'plink', 'magenpy'},
                    help="Type of summary statistics file")
args = parser.parse_args()

h2g = []
pc = []

for chrom in range(1, 23):

    snp_effects_file = osp.join(args.output_dir, f"chr_{chrom}.snpRes")
    hyperparams_file = osp.join(args.output_dir, f"chr_{chrom}.parRes")
    sumstats_file = osp.join(args.ss_dir, f"chr_{chrom}.ma")

    # Read the SNP effects file:
    snp_effect_df = pd.read_csv(snp_effects_file, delim_whitespace=True)
    snp_effect_df = snp_effect_df[['Chrom', 'Name', 'PIP', 'A1Effect']]
    snp_effect_df.columns = ['CHR', 'SNP', 'PIP', 'BETA']

    # Read the summary statistics table:
    if args.type == 'plink':
        ss_table = pd.read_csv(sumstats_file, delim_whitespace=True)[['SNP', 'A1', 'A2']]
    else:
        ss_table = pd.read_csv(sumstats_file, delim_whitespace=True)[['ID', 'ALT', 'REF']]
        ss_table.columns = ['SNP', 'A1', 'A2']

    # Merge the summary statistics table with the output table:
    snp_effect_df = snp_effect_df.merge(ss_table, how='right')
    snp_effect_df.fillna(0., inplace=True)

    snp_effect_df = snp_effect_df[['CHR', 'SNP', 'A1', 'A2', 'PIP', 'BETA']]
    snp_effect_df.to_csv(snp_effects_file.replace('.snpRes', '.fit'), sep="\t", index=False)

    # --------------------------------------------- #
    # Transform the hyperparameter estimates:

    params = pd.read_csv(hyperparams_file, delim_whitespace=True, skiprows=1)
    heritability = params.loc['hsq', 'Mean']
    prop_causal = snp_effect_df['PIP'].mean()

    h2g.append(heritability)
    pc.append(prop_causal)

    hyp_df = pd.DataFrame.from_dict({
            'Heritability': heritability,
            'Prop. Causal': prop_causal
        }, orient='index')

    hyp_df.to_csv(hyperparams_file.replace('.parRes', '.hyp'))

combined_hyp_df = pd.DataFrame.from_dict({
            'Heritability': sum(h2g),
            'Prop. Causal': np.mean(pc)
        }, orient='index')

combined_hyp_df.to_csv(osp.join(args.output_dir, 'combined.hyp'))

