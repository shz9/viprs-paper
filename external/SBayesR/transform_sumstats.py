import pandas as pd
import argparse

parser = argparse.ArgumentParser(description='Transform summary statistics to COJO format')

parser.add_argument('-s', '--sumstats', dest='ss_file', type=str, required=True,
                    help='The summary statistics files')
parser.add_argument('-t', '--type', dest='type', type=str, default='plink',
                    choices={'plink', 'pystatgen'})
args = parser.parse_args()

# Read the sumstats file:
ss_df = pd.read_csv(args.ss_file, sep="\t")

if args.type == 'pystatgen':
    ss_df = ss_df[['SNP', 'A1', 'A2', 'MAF', 'BETA', 'SE', 'PVAL', 'N']]
elif args.type == 'plink':
    ss_df['A2'] = ss_df.apply(lambda x: [x['ALT1'], x['REF']][x['A1'] == x['ALT1']], axis=1)
    ss_df = ss_df[['ID', 'A1', 'A2', 'A1_FREQ', 'BETA', 'SE', 'P', 'OBS_CT']]

# Write the results to the same directory:
ss_df.columns = ['SNP', 'A1', 'A2', 'freq', 'b', 'se', 'p', 'n']
ss_df.to_csv(args.ss_file.replace(".PHENO1.glm.linear", ".ma"), sep="\t", index=False)
