import pandas as pd
import numpy as np
import argparse


parser = argparse.ArgumentParser(description='Output a list of SNPs to exclude from the analysis')

parser.add_argument('-s', '--ss_file', dest='ss_file', type=str, required=True,
                    help='The summary statistics file')
parser.add_argument('-f', '--her_file', dest='her_file', type=str, required=True,
                    help='The per-SNP heritability file')
args = parser.parse_args()

df1 = pd.read_csv(args.ss_file, delim_whitespace=True)
df2 = pd.read_csv(args.her_file, delim_whitespace=True)

merged_table = df1.merge(df2, on='Predictor')

# Detect cases where the correct allele is specified in both tables:
matching_allele = np.all(merged_table[['A1_x', 'A2_x']].values == merged_table[['A1_y', 'A2_y']].values, axis=1)

# Detect cases where the effect and reference alleles are flipped:
flip = np.all(merged_table[['A2_x', 'A1_x']].values == merged_table[['A1_y', 'A2_y']].values, axis=1)

# Keep SNPs with wrong alleles:
merged_table = merged_table.loc[~(matching_allele | flip), ]
merged_table[['Predictor']].to_csv(args.ss_file.replace(".megaprs.ss", ".exclude"),
                                   index=False, header=False, sep='\t')
