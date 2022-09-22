import pandas as pd
import argparse


parser = argparse.ArgumentParser(description='Transform a predictor to rsID')

parser.add_argument('-f', '--file', dest='pred_file', type=str, required=True,
                    help='The MegaPRS effect file')
args = parser.parse_args()

eff_df = pd.read_csv(args.pred_file, delim_whitespace=True)
models_cols = [c for c in eff_df.columns if c not in ('Predictor', 'A1', 'A2')]
eff_df[['CHR', 'POS']] = eff_df['Predictor'].str.split(':', 1, expand=True)
eff_df['CHR'] = eff_df['CHR'].astype(int)
eff_df['POS'] = eff_df['POS'].astype(int)

chroms = eff_df['CHR'].unique()

bim_dfs = pd.concat([pd.read_csv(f"data/ukbb_qc_genotypes/chr_{c}.bim", delim_whitespace=True,
                                 names=['CHR', 'SNP', 'cM', 'POS', 'A1', 'A2'],
                                 dtype={
                                     'CHR': int,
                                     'SNP': str,
                                     'cM': float,
                                     'POS': int,
                                     'A1': str,
                                     'A2': str
                                 })[['CHR', 'SNP', 'POS']] for c in chroms])
merged_df = eff_df.merge(bim_dfs, on=['CHR', 'POS'])
merged_df[['SNP', 'A1', 'A2'] + models_cols].to_csv(args.pred_file, index=False, sep="\t")
