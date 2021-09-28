import pandas as pd
import numpy as np
import argparse
import os.path as osp

parser = argparse.ArgumentParser(description='Transform output of PRSice2')

parser.add_argument('-o', '--output', dest='output_dir', type=str, required=True,
                    help='The directory where the PRSice2 output files reside')
parser.add_argument('-s', '--sumstats', dest='ss_dir', type=str, required=True,
                    help='The summary statistics files')
parser.add_argument('-t', '--type', dest='type', type=str, default='plink',
                    choices={'plink', 'pystatgen'},
                    help="Type of summary statistics file")
args = parser.parse_args()

for chrom in range(1, 23):
    # Read the clumped SNPs:
    clumped_snps = pd.read_csv(osp.join(args.output_dir, f"chr_{chrom}.snp"), sep="\s+")

    # Read the best fit model and extract the best P-value threshold...
    best_fit = pd.read_csv(osp.join(args.output_dir, f"chr_{chrom}.summary"), sep="\s+")
    best_p_threshold = best_fit['Threshold'][0]

    # Read the summary statistics table:
    ss_table = pd.read_csv(osp.join(args.ss_dir, f"chr_{chrom}.PHENO1.glm.linear"), sep="\s+")

    if args.type == 'plink':
        ss_table['A2'] = ss_table.apply(lambda x: [x['ALT1'], x['REF']][x['A1'] == x['ALT1']], axis=1)
        ss_table = ss_table.rename(columns={'ID': 'SNP', '#CHROM': 'CHR', 'P': 'PVAL'})

    # Merge the summary statistics table with the clumped SNPs table:
    merged_df = clumped_snps.merge(ss_table, how='right')

    # Set the BETAs for the clumped/filtered SNPs to zero:
    merged_df['BETA'] = ((~merged_df['P'].isna()) &
                         (merged_df['PVAL'] <= best_p_threshold)).astype(int) * merged_df['BETA']
    merged_df['PIP'] = np.nan

    # Output a .fit file for evaluation on the testing set:
    final_df = merged_df[['CHR', 'SNP', 'A1', 'A2', 'PIP', 'BETA']]
    final_df.to_csv(osp.join(args.output_dir, f"chr_{chrom}.fit"), sep="\t", index=False, na_rep='NA')
