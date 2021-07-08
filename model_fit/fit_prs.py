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
from vemPRS.prs.src.vem_c import vem_prs
from vemPRS.prs.src.vem_c_sbayes import vem_prs_sbayes
from vemPRS.prs.src.gibbs_c import prs_gibbs
from vemPRS.prs.src.gibbs_c_sbayes import prs_gibbs_sbayes
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

parser.add_argument('-m', '--model', dest='model', type=str, default='vem_c',
                    help='The PRS model to fit', choices={'VIPRS', 'VIPRSSBayes', 'GibbsPRS', 'GibbsPRSSBayes',
                                                          'gibbs_c', 'vem_c', 'vem_c_sbayes', 'prs_gibbs_sbayes'})
parser.add_argument('-f', '--fitting-strategy', dest='fitting_strategy', type=str, default='EM',
                    help='The strategy for fitting the hyperparameters', choices={'EM', 'BO', 'GS', 'BMA'})
parser.add_argument('-l', '--ld-panel', dest='ld_panel', type=str, default='ukbb_50k_windowed',
                    help='The LD panel to use in model fit')
parser.add_argument('-s', '--sumstats', dest='ss_file', type=str, required=True,
                    help='The summary statistics file')

args = parser.parse_args()

sumstats_file = args.ss_file
chrom = osp.basename(sumstats_file).split(".")[0]

if 'sample' in args.ld_panel:
    load_ld = False
    ld_panel = f"data/ld/{args.ld_panel}/ld/{chrom}"
else:
    load_ld = True
    ld_panel = f"data/ld/{args.ld_panel}/ld_ragged/{chrom}"


print("> Loading the LD data and associated summary statistics file...")

gdl = GWASDataLoader(f"data/ukbb_qc_genotypes/{chrom}.bed",
                     keep_individuals="data/keep_files/ukbb_train_subset.keep",
                     ld_store_files=ld_panel,
                     sumstats_file=sumstats_file)

if args.model == 'vem_c':
    m = vem_prs(gdl, load_ld=load_ld)
elif args.model == 'gibbs_c':
    m = prs_gibbs(gdl, load_ld=load_ld)
elif args.model == 'vem_c_sbayes':
    m = vem_prs_sbayes(gdl, load_ld=load_ld)
elif args.model == 'prs_gibbs_sbayes':
    m = prs_gibbs_sbayes(gdl, load_ld=load_ld)
elif args.model == 'VIPRS':
    m = VIPRS(gdl, load_ld=load_ld)
elif args.model == 'VIPRSSBayes':
    m = VIPRSSBayes(gdl, load_ld=load_ld)
elif args.model == 'GibbsPRS':
    m = GibbsPRS(gdl, load_ld=load_ld)
elif args.model == 'GibbsPRSSBayes':
    m = GibbsPRSSBayes(gdl, load_ld=load_ld)


#### Fit the model to the data: ####
print("> Performing model fit...")

# TODO: Change the exception handling logic.

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

#### Writing out the output ####

print("> Writing out the inference results...")

if args.fitting_strategy == 'EM':
    output_dir = f"data/model_fit/{args.ld_panel}/{args.model}/"
else:
    output_dir = f"data/model_fit/{args.ld_panel}/{args.model}-{args.fitting_strategy}/"

output_f = osp.join(output_dir, sumstats_file.replace("data/gwas/", '').replace('.PHENO1.glm.linear', '.fit'))
makedir(osp.dirname(output_f))

if args.fitting_strategy == 'BMA':

    # Write inferred model parameters:
    dfs = []
    for c in gdl.shapes:
        dfs.append(
            pd.DataFrame({'CHR': c,
                          'SNP': gdl.snps[c],
                          'PIP': m[0][c],
                          'BETA': m[0][c]*m[1][c]})
        )

    dfs = pd.concat(dfs)
    dfs.to_csv(output_f, sep="\t", index=False)

else:
    # Write inferred model parameters:
    m.write_inferred_params(output_f)

    # Write inferred hyperparameters:

    hyp_df = pd.DataFrame.from_dict({
        'Heritability': m.get_heritability(),
        'Prop. Causal': m.get_proportion_causal()
    }, orient='index')

    hyp_df.to_csv(output_f.replace('.fit', '.hyp'))
