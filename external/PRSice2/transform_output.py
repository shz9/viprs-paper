import pandas as pd
import numpy as np
import sys

prsice_prefix = sys.argv[1]
sumstats_file = sys.argv[2]

# Read the clumped SNPs:
clumped_snps = pd.read_csv(prsice_prefix + ".snp", sep="\s+")

# Read the best fit model and extract the best P-value threshold...
best_fit = pd.read_csv(prsice_prefix + ".summary", sep="\s+")
best_p_threshold = best_fit['Threshold'][0]

# Read the summary statistics table:
ss_table = pd.read_csv(sumstats_file, sep="\s+")

# Merge the summary statistics table with the clumped SNPs table:
merged_df = clumped_snps.merge(ss_table, how='right')

# Set the BETAs for the clumped/filtered SNPs to zero:
merged_df['BETA'] = ((~merged_df['P'].isna()) & (merged_df['PVAL'] <= best_p_threshold)).astype(int) * merged_df['BETA']
merged_df['PIP'] = np.nan

# Output a .fit file for evaluation on the testing set:
final_df = merged_df[['CHR', 'SNP', 'PIP', 'BETA']]
final_df.to_csv(prsice_prefix + ".fit", sep="\t")
