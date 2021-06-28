"""
Author: Shadi Zabad
Date: May 2021
"""

import sys
import os.path as osp
import pandas as pd
sys.path.append(osp.dirname(osp.dirname(__file__)))
sys.path.append("vemPRS/")
from gwasimulator.GWASDataLoader import GWASDataLoader
from vemPRS.prs.src.PRSModel import PRSModel
from utils import makedir
import argparse
import functools
print = functools.partial(print, flush=True)


parser = argparse.ArgumentParser(description='Generate Polygenic Scores')

parser.add_argument('-f', '--fit-file', dest='fit_file', type=str, required=True,
                    help='The file with the outputted parameter fits')
args = parser.parse_args()

chrom = osp.basename(args.fit_file).replace('.fit', '')

test_data = GWASDataLoader(f"data/ukbb_qc_genotypes/{chrom}.bed",
                           keep_individuals="data/keep_files/ukbb_test_subset.keep",
                           compute_ld=False)
prs_m = PRSModel(test_data)
prs_m.read_inferred_params(args.fit_file)

# Predict on the test set:
print("> Generating polygenic scores...")
prs = prs_m.predict()

print("> Saving results...")
# Save the PRS for this chromosome as a table:
genotype_data = next(iter(test_data.genotypes.values()))['G']

ind_table = pd.DataFrame({
    'FID': genotype_data.sample.fid.values,
    'IID': genotype_data.sample.iid.values,
    'PRS': prs
})

# Output the scores:
output_dir = osp.dirname(args.fit_file).replace("model_fit", "test_scores")
makedir(output_dir)
ind_table.to_csv(osp.join(output_dir, chrom + ".prs"),
                 index=False, sep="\t")

