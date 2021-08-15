"""
Author: Shadi Zabad
Date: May 2021
"""

import sys
import os
import os.path as osp
import glob
import numpy as np
import pandas as pd
from zarr import blosc
sys.path.append(osp.dirname(osp.dirname(__file__)))
sys.path.append("vemPRS/")
from gwasimulator.GWASDataLoader import GWASDataLoader
from vemPRS.prs.src.VIPRS import VIPRS
from vemPRS.prs.src.VIPRSSBayes import VIPRSSBayes
from vemPRS.prs.src.GibbsPRS import GibbsPRS
from vemPRS.prs.src.GibbsPRSSBayes import GibbsPRSSBayes
from vemPRS.prs.src.HyperparameterSearch import BMA, GridSearch, BayesOpt
from utils import makedir
import argparse
import functools
print = functools.partial(print, flush=True)


def main():

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

    file_sets = []

    if args.genomewide:
        file_sets.append({
            'LD': ld_panel_files,
            'SS': ss_files
        })
    else:
        for ldf, ssf in zip(ld_panel_files, ss_files):
            file_sets.append({
                'LD': ldf,
                'SS': ssf
            })

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

    if args.fitting_strategy in ('BMA', 'GS'):
        load_ld = True
        max_iter = 100
    elif 'sample' in args.ld_panel:
        load_ld = True
        max_iter = 500
    else:
        load_ld = True
        max_iter = 1000

    h2g = []
    prop_causal = []

    for fs in file_sets:

        print("- - - - - - - - - - - - - - - - - - - -")

        gdl = GWASDataLoader(ld_store_files=fs['LD'],
                             sumstats_files=fs['SS'],
                             sumstats_format='plink',
                             temp_dir=os.getenv('SLURM_TMPDIR', 'temp'))

        if load_ld:
            gdl.load_ld()

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
                m = BayesOpt(gdl, m)
            elif args.fitting_strategy == 'GS':
                m = GridSearch(gdl, m, n_proc=10)
            elif args.fitting_strategy == 'BMA':
                m = BMA(gdl, m, n_proc=10)

            m = m.fit(max_iter=max_iter)
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

        if not args.genomewide and args.fitting_strategy != 'BMA':

            # Write the per-chromosome estimates:
            chrom = gdl.chromosomes[0]
            pd.DataFrame.from_dict({
                'Heritability': m_h2g,
                'Prop. Causal': m_p
            }, orient='index').to_csv(osp.join(output_dir, f'chr_{chrom}.hyp'))

        if load_ld:
            gdl.release_ld()

        gdl.cleanup()

        if args.fitting_strategy != 'BMA':
            h2g.append(m_h2g)
            prop_causal.append(m_p)

    if args.fitting_strategy != 'BMA':
        if np.sum(h2g) > 1.:
            print("Warning: The estimated heritability has a value greater than 1. "
                  "This is indicative of poor model fit or the algorithm diverging. "
                  "You may need to re-run this model with a different LD panel.")

        hyp_df = pd.DataFrame.from_dict({
            'Heritability': np.sum(h2g),
            'Prop. Causal': np.mean(prop_causal)
        }, orient='index')

        hyp_df.to_csv(osp.join(output_dir, 'combined.hyp'))


if __name__ == '__main__':
    main()
