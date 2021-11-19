import sys
import os
import os.path as osp
import glob
import numpy as np
import pandas as pd
import re
sys.path.append(osp.dirname(osp.dirname(__file__)))
sys.path.append("vemPRS/")
from gwasimulator.GWASDataLoader import GWASDataLoader
from vemPRS.prs.src.VIPRS import VIPRS
from vemPRS.prs.src.VIPRSAlpha import VIPRSAlpha
from vemPRS.prs.src.VIPRSSBayes import VIPRSSBayes
from vemPRS.prs.src.VIPRSMultiCohort import VIPRSMultiCohort
from vemPRS.prs.src.HyperparameterSearch import BMA, GridSearch, BayesOpt
from utils import makedir
import argparse
import functools
print = functools.partial(print, flush=True)


parser = argparse.ArgumentParser(description='Fit PRS models iteratively')
parser.add_argument('-s', '--sumstats', dest='ss_dir', nargs='+', required=True,
                    help='The summary statistics directory')
parser.add_argument('-l', '--ld-panel', dest='ld_panel', type=str, default='ukbb_50k_windowed',
                    help='The LD panel to use in model fit')
parser.add_argument('--sumstats-format', dest='sumstats_format', type=str, default='LDSC',
                    help='The format for the summary statistics')

args = parser.parse_args()

chr_gdls = {chrom: [] for chrom in range(1, 23)}

for ss_dir in args.ss_dir:
    for chrom in range(1, 23):
        chr_gdls[chrom].append(GWASDataLoader(ld_store_files=f"data/ld/{args.ld_panel}/ld/chr_{chrom}",
                               sumstats_files=osp.join(ss_dir, "combined.sumstats"),
                               sumstats_format=args.sumstats_format,
                               temp_dir=os.getenv('SLURM_TMPDIR', 'temp')))

for c, gdls in chr_gdls.items():
    prs_models = [VIPRS(gdl) for gdl in gdls]

    vmc = VIPRSMultiCohort(prs_models)
    vmc.fit()


