"""
Author: Shadi Zabad
Date: July 2021
"""

import sys
import os.path as osp
sys.path.append(osp.dirname(osp.dirname(__file__)))
import glob
import pandas as pd
from sklearn.model_selection import KFold, StratifiedKFold, train_test_split
from utils import makedir
import argparse
import functools
print = functools.partial(print, flush=True)


parser = argparse.ArgumentParser(description='Generate cross validation folds')

parser.add_argument('-t', dest='type', type=str, default='quantitative',
                    choices={'quantitative', 'binary'},
                    help='The class of phenotypes.')
parser.add_argument('-n', dest='folds', type=int, default=5,
                    help="Number of folds")
parser.add_argument('-p', dest='valid_prop', type=float, default=.1,
                    help="Proportion of training samples reserved for validation")

args = parser.parse_args()

n_folds = args.folds
validation_prop = args.valid_prop
ind_keep_file = "data/keep_files/ukbb_qc_individuals.keep"
phenotype_dir = f"data/phenotypes/{args.type}/real/"
output_dir = f"data/keep_files/ukbb_cv/{args.type}"

print(f"> Generating Cross-Validation folds for {args.type} real phenotypes.")
print("Number of folds:", n_folds)
print("Proportion of training samples used for validation:", validation_prop)

# Read the list of individuals that passed the QC filters:
ind_df = pd.read_csv(ind_keep_file, sep="\s+", names=['FID', 'IID'])

for pheno_file in glob.glob(osp.join(phenotype_dir, "*.txt")):

    trait = osp.basename(pheno_file).replace(".txt", "")
    print(f"Generating CV folds for {trait}")

    phe_output_dir = osp.join(output_dir, trait)

    # Read the phenotype file:
    phe_df = pd.read_csv(pheno_file, sep="\t", names=['FID', 'IID', 'phenotype'])

    # Merge the QC'ed individuals table with the phenotype table
    # and individuals with missing phenotype measurements:
    phe_df = phe_df.merge(ind_df)
    phe_df.dropna(inplace=True)

    # Initialize the K-Fold object and generate the
    # training/testing indices for each fold:

    if args.type == 'binary':
        kf = StratifiedKFold(n_splits=n_folds, shuffle=True)
        splits = enumerate(kf.split(phe_df[['FID', 'IID']], phe_df[['phenotype']]), 1)
    else:
        kf = KFold(n_splits=n_folds, shuffle=True)
        splits = enumerate(kf.split(phe_df), 1)

    for i, (train_idx, test_idx) in splits:

        # Create a subfolder for this fold:
        fold_output_dir = osp.join(phe_output_dir, f'fold_{i}')
        makedir(fold_output_dir)

        # Obtain the train, validation, test subsets:
        # Note: the validation is currently set to be 10% of the training set:
        test_subset = phe_df.iloc[test_idx, [0, 1]]
        if args.type == 'binary':
            train_subset, validation_subset = train_test_split(phe_df.iloc[train_idx, [0, 1]],
                                                               test_size=validation_prop,
                                                               stratify=phe_df['phenotype'].values[train_idx])
        else:
            train_subset, validation_subset = train_test_split(phe_df.iloc[train_idx, [0, 1]],
                                                               test_size=validation_prop)

        # Output the subsets to keep files:
        train_subset.to_csv(osp.join(fold_output_dir, 'train.keep'), index=False, header=False, sep="\t")
        test_subset.to_csv(osp.join(fold_output_dir, 'test.keep'), index=False, header=False, sep="\t")
        validation_subset.to_csv(osp.join(fold_output_dir, 'validation.keep'), index=False, header=False, sep="\t")

