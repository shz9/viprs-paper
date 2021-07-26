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

ss_dir = osp.normpath(args.ss_dir)  # Get the summary statistics directory
config = osp.basename(osp.dirname(ss_dir))
trait = osp.basename(ss_dir)

print("> Processing GWAS summary statistics in:", ss_dir)
print("> Loading the LD data and associated summary statistics file...")

ss_files = sorted(glob.glob(osp.join(ss_dir, "*.linear")),
                  key=lambda x: int(osp.basename(x).split('.')[0].split('_')[1]))
ld_panel_files = [f"data/ld/{args.ld_panel}/ld/{osp.basename(ssf).split('.')[0]}" for ssf in ss_files]

gdls = []

if args.genomewide:
    gdls.append(GWASDataLoader(ld_store_files=ld_panel_files, sumstats_files=ss_files, sumstats_format='plink'))
else:
    for ldf, ssf in zip(ld_panel_files, ss_files):
        print("Constructing a GDL for:", ssf)
        gdls.append(GWASDataLoader(ld_store_files=ldf, sumstats_files=ssf, sumstats_format='plink'))


if args.fitting_strategy == 'EM':
    output_dir = f"data/model_fit/{args.ld_panel}/{args.model}"
else:
    output_dir = f"data/model_fit/{args.ld_panel}/{args.model}-{args.fitting_strategy}"

if args.genomewide:
    output_dir = osp.join(output_dir + "-genomewide", config, trait)
else:
    output_dir = osp.join(output_dir, config, trait)

print("> Storing model fit results in:", output_dir)
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
    if args.genomewide:
        print("> Performing model fit on all chromosomes jointly...")
    else:
        print("> Performing model fit on chromosome:", gdl.chromosomes)

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

    # Write the estimated hyperparameters:
    m_h2g = m.get_heritability()
    m_p = m.get_proportion_causal()

    if not args.genomewide:
        # Write the per-chromosome estimates:
        chrom = gdl.chromosomes[0]
        pd.DataFrame.from_dict({
            'Heritability': m_h2g,
            'Prop. Causal': m_p
        }, orient='index').to_csv(osp.join(output_dir, f'chr_{chrom}.hyp'))

    h2g.append(m_h2g)
    prop_causal.append(m_p)


if np.sum(h2g) > 1.:
    print("Warning: The estimated heritability has a value greater than 1. This is indicative of poor model fit or "
          "the algorithm diverging. You may need to re-run this model with a different LD panel.")

hyp_df = pd.DataFrame.from_dict({
    'Heritability': np.sum(h2g),
    'Prop. Causal': np.mean(prop_causal)
}, orient='index')

hyp_df.to_csv(osp.join(output_dir, 'combined.hyp'))
