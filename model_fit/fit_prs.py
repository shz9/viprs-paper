"""
Author: Shadi Zabad
Date: May 2021
"""

import sys
import os.path as osp
import glob
import numpy as np
import pandas as pd
sys.path.append(osp.dirname(osp.dirname(__file__)))
sys.path.append("vemPRS/")
from gwasimulator.GWASDataLoader import GWASDataLoader
from vemPRS.prs.src.VIPRS import VIPRS
from vemPRS.prs.src.VIPRSSBayes import VIPRSSBayes
from vemPRS.prs.src.GibbsPRS import GibbsPRS
from vemPRS.prs.src.GibbsPRSSBayes import GibbsPRSSBayes
from vemPRS.prs.src.HyperparameterSearch import HyperparameterSearch, fit_model_averaging
from utils import makedir
import argparse
import functools
print = functools.partial(print, flush=True)

parser = argparse.ArgumentParser(description='Fit PRS models')

parser.add_argument('-m', '--model', dest='model', type=str, default='VIPRS',
                    help='The PRS model to fit', choices={'VIPRS', 'VIPRSSBayes', 'GibbsPRS', 'GibbsPRSSBayes'})
parser.add_argument('-f', '--fitting-strategy', dest='fitting_strategy', type=str, default='EM',
                    help='The strategy for fitting the hyperparameters', choices={'EM', 'BO', 'GS', 'BMA'})
parser.add_argument('-l', '--ld-panel', dest='ld_panel', type=str, default='ukbb_50k_windowed',
                    help='The LD panel to use in model fit')
parser.add_argument('-s', '--sumstats', dest='ss_dir', type=str, required=True,
                    help='The summary statistics directory')
parser.add_argument('--genomewide', dest='genomewide', action='store_true', default=False,
                    help='Fit all chromosomes jointly')

args = parser.parse_args()

config = osp.basename(osp.dirname(args.ss_dir))
trait = osp.basename(args.ss_dir)

print("> Loading the LD data and associated summary statistics file...")

ss_files = glob.glob(osp.join(args.ss_dir, "*.linear"))
ld_panel_files = [f"data/ld/{args.ld_panel}/ld/{osp.basename(ssf).split('.')[0]}" for ssf in ss_files]

gdls = []

if args.genomewide:
    gdls.append(GWASDataLoader(ld_store_files=ld_panel_files, sumstats_files=ss_files))
else:
    for ldf, ssf in zip(ld_panel_files, ss_files):
        gdls.append(GWASDataLoader(ld_store_files=ldf, sumstats_files=ssf))


if args.fitting_strategy == 'EM':
    output_dir = f"data/model_fit/{args.ld_panel}/{args.model}"
else:
    output_dir = f"data/model_fit/{args.ld_panel}/{args.model}-{args.fitting_strategy}"

if args.genomewide:
    output_dir = osp.join(output_dir + "-genomewide", config, trait)
else:
    output_dir = osp.join(output_dir, config, trait)

makedir(output_dir)

if 'sample' in args.ld_panel:
    load_ld = False
else:
    load_ld = True

h2g = []
prop_causal = []

for gdl in gdls:

    if args.model == 'VIPRS':
        m = VIPRS(gdl, load_ld=load_ld)
    elif args.model == 'VIPRSSBayes':
        m = VIPRSSBayes(gdl, load_ld=load_ld)
    elif args.model == 'GibbsPRS':
        m = GibbsPRS(gdl, load_ld=load_ld)
    elif args.model == 'GibbsPRSSBayes':
        m = GibbsPRSSBayes(gdl, load_ld=load_ld)

    # Fit the model to the data:
    print("> Performing model fit...")

    try:
        if args.fitting_strategy == 'BO':
            hs = HyperparameterSearch(m)
            m = hs.fit_bayes_opt(opt_params=('sigma_epsilon', ))
        elif args.fitting_strategy == 'GS':
            hs = HyperparameterSearch(m)
            m = hs.fit_grid_search(opt_params=('sigma_epsilon', ), n_steps=20)
        elif args.fitting_strategy == 'BMA':
            m = fit_model_averaging(m)
        else:
            m = m.fit()
    except Exception as e:
        print(e)
        if e.__class__.__name__ != 'OptimizationDivergence':
            raise e

    print("> Writing out the inference results...")

    # Write inferred model parameters:
    m.write_inferred_params(output_dir, per_chromosome=True)

    # Save inferred hyperparameters:
    h2g.append(m.get_heritability())
    prop_causal.append(m.get_proportion_causal())

hyp_df = pd.DataFrame.from_dict({
    'Heritability': np.sum(h2g),
    'Prop. Causal': np.mean(prop_causal)
}, orient='index')

hyp_df.to_csv(osp.join(output_dir, 'combined.hyp'))
