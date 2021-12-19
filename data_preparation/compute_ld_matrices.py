"""
Author: Shadi Zabad
Date: April 2021
"""

import sys
import os
import os.path as osp
sys.path.append(osp.dirname(osp.dirname(__file__)))
import argparse
from gwasimulator.GWASDataLoader import GWASDataLoader


parser = argparse.ArgumentParser(description='Computing LD matrices')

parser.add_argument('--panel-name', dest='name', type=str, required=True)
parser.add_argument('--estimator', dest='estimator', type=str, default='windowed',
                    help='The LD estimator (windowed, shrinkage, sample)')
parser.add_argument('--bfile', dest='bed_file', type=str, default="data/ukbb_qc_genotypes/chr_22",
                    help='The path to the BED file')
parser.add_argument('--keep-file', dest='keep_file', type=str, default=None,
                    help='A keep file for individuals used to compute the LD matrices')

args = parser.parse_args()

if args.estimator == 'windowed':
    gdl = GWASDataLoader(args.bed_file,
                         keep_individuals=args.keep_file,
                         ld_estimator="windowed",
                         window_unit="cM",
                         cm_window_cutoff=3.,
                         min_mac=5,
                         min_maf=0.01,
                         compute_ld=True,
                         output_dir=f"data/ld/{args.name}_windowed/",
                         temp_dir=os.getenv('SLURM_TMPDIR', 'temp'))
if args.estimator == 'block':
    gdl = GWASDataLoader(args.bed_file,
                         keep_individuals=args.keep_file,
                         ld_estimator="block",
                         ld_block_files='metadata/ldetect_blocks.txt',
                         min_mac=5,
                         min_maf=0.01,
                         compute_ld=True,
                         output_dir=f"data/ld/{args.name}_block/",
                         temp_dir=os.getenv('SLURM_TMPDIR', 'temp'))
elif args.estimator == 'shrinkage':
    gdl = GWASDataLoader(args.bed_file,
                         keep_individuals=args.keep_file,
                         ld_estimator="shrinkage",
                         genmap_Ne=11400,
                         genmap_sample_size=183,
                         shrinkage_cutoff=1e-5,
                         min_mac=5,
                         min_maf=0.01,
                         compute_ld=True,
                         output_dir=f"data/ld/{args.name}_shrinkage/",
                         temp_dir=os.getenv('SLURM_TMPDIR', 'temp'))
elif args.estimator == 'sample':
    gdl = GWASDataLoader(args.bed_file,
                         keep_individuals=args.keep_file,
                         ld_estimator="sample",
                         min_mac=5,
                         min_maf=0.01,
                         compute_ld=True,
                         output_dir=f"data/ld/{args.name}_sample/",
                         temp_dir=os.getenv('SLURM_TMPDIR', 'temp'))
else:
    raise Exception(f"LD estimator {args.estimator} not implemented!")

# Clean up all intermediate files and directories:
gdl.cleanup()
