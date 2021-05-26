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
from utils import makedir
import argparse

parser = argparse.ArgumentParser(description='Fit PRS models')

parser.add_argument('-m', '--model', dest='model', type=str, default='vem_c',
                    help='The PRS model to fit', choices={'VIPRS', 'VIPRSSBayes', 'GibbsPRS', 'GibbsPRSSBayes',
                                                          'gibbs_c', 'vem_c', 'vem_c_sbayes', 'prs_gibbs_sbayes'})
parser.add_argument('-l', '--ld-panel', dest='ld_panel', type=str, default='ukbb_windowed',
                    help='The LD panel to use in model fit', choices={'ukbb_windowed', 'ukbb_shrinkage', 'ukbb_sample'})
parser.add_argument('-s', '--sumstats', dest='ss_file', type=str, required=True,
                    help='The summary statistics file')

args = parser.parse_args()

ld_panels = {
    'ukbb_windowed': 'data/ld/ukbb_windowed/ld_ragged/chr_22',
    'ukbb_shrinkage': 'data/ld/ukbb_shrinkage/ld_ragged/chr_22',
    'ukbb_sample': 'data/ld/ukbb_sample/ld/chr_22'
}

sumstats_file = args.ss_file

output_dir = f"data/model_fit/{args.ld_panel}/{args.model}/"
output_f = osp.join(output_dir, sumstats_file.replace("data/gwas/", '').replace('.PHENO1.glm.linear', '.fit'))

gdl = GWASDataLoader("data/ukbb_qc_genotypes/chr_22.bed",
                     keep_individuals="data/keep_files/ukbb_train_subset.keep",
                     ld_store_files=ld_panels[args.ld_panel],
                     sumstats_file=sumstats_file)

if 'sample' in args.ld_panel:
    load_ld = False
else:
    load_ld = True

makedir(osp.dirname(output_f))

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

# Fit the model to the data:
m.fit()

# Write inferred model parameters:
m.write_inferred_params(output_f)

# Write inferred hyperparameters:

hyp_df = pd.DataFrame.from_dict({
    'Heritability': m.get_heritability(),
    'Prop. Causal': m.get_proportion_causal()
}, orient='index')

hyp_df.to_csv(output_f.replace('.fit', '.hyp'))
