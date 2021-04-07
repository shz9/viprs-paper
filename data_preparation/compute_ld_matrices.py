"""
Author: Shadi Zabad
Date: April 2021
"""

import sys
import os.path as osp
sys.path.append(osp.dirname(osp.dirname(__file__)))
import argparse
from gwasimulator.GWASDataLoader import GWASDataLoader


parser = argparse.ArgumentParser(description='Computing LD matrices')

parser.add_argument('--estimator', dest='estimator', type=str, default='windowed',
                    help='The LD estimator (windowed, shrinkage, sample)')
parser.add_argument('--chr', dest='chr', type=int, default=None,
                    help='The chromosome for which to calculate LD')

args = parser.parse_args()

if args.chr is None:
    bed_dir = "data/ukbb_qc_genotypes/chr_"
else:
    bed_dir = f"data/ukbb_qc_genotypes/chr_{args.chr}"

if args.estimator == 'windowed':
    GWASDataLoader(bed_dir,
                   ld_subset_samples="data/keep_files/ukbb_ld_subset.keep",
                   ld_estimator="windowed",
                   window_unit="cM",
                   cm_window_cutoff=1.,
                   compute_ld=True,
                   sparse_ld=True,
                   temp_dir="data/ld/ukbb_windowed/")
elif args.estimator == 'shrinkage':
    GWASDataLoader(bed_dir,
                   ld_subset_samples="data/keep_files/ukbb_ld_subset.keep",
                   ld_estimator="shrinkage",
                   genmap_Ne=11400,
                   genmap_sample_size=183,
                   shrinkage_cutoff=1e-3,
                   compute_ld=True,
                   sparse_ld=True,
                   temp_dir="data/ld/ukbb_shrinkage/")
else:
    raise Exception(f"LD estimator {args.estimator} not implemented!")
