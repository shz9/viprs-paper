import pandas as pd
import numpy as np
import os.path as osp
import argparse


parser = argparse.ArgumentParser(description='Transform output of MegaPRS')

parser.add_argument('-o', '--output', dest='output_dir', type=str, required=True,
                    help='The directory where the MegaPRS output files reside')
args = parser.parse_args()

for chrom in range(1, 23):
    ss_df = pd.read_csv(osp.join(args.output_dir, f"chr_{chrom}.val.best.effects"),
                        delim_whitespace=True)

    model_name = ss_df.columns[-1]
    ss_df.rename({'Predictor': 'SNP', model_name: 'BETA'}, axis=1, inplace=True)
    ss_df['CHR'] = chrom
    ss_df['PIP'] = np.nan

    ss_df = ss_df[['CHR', 'SNP', 'A1', 'A2', 'PIP', 'BETA']]

    ss_df.to_csv(osp.join(args.output_dir, f"chr_{chrom}.fit"),
                 sep="\t", index=False, na_rep='NA')
