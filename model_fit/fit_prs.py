"""
Author: Shadi Zabad
Date: May 2021
"""

import sys
import os.path as osp
sys.path.append(osp.dirname(osp.dirname(__file__)))
sys.path.append("vemPRS/")
from gwasimulator.GWASDataLoader import GWASDataLoader
from vemPRS.prs.src.vem_c import vem_prs
from vemPRS.prs.src.gibbs_c import prs_gibbs
from utils import makedir
import argparse

parser = argparse.ArgumentParser(description='Fit PRS models')

parser.add_argument('-m', '--model', dest='model', type=str, default='vem_c',
                    help='The PRS model to fit', choices={'gibbs_c', 'vem_c'})
parser.add_argument('-s', '--sumstats', dest='ss_file', type=str, required=True,
                    help='The summary statistics file')

args = parser.parse_args()

sumstats_file = args.ss_file

output_dir = f"data/model_fit/{args.model}/"
output_f = osp.join(output_dir, sumstats_file.replace("data/gwas/", '').replace('.PHENO1.glm.linear', '.fit'))

gdl = GWASDataLoader("data/ukbb_qc_genotypes/chr_22.bed",
                     ld_store_files="data/ld/ukbb_windowed/ld_ragged/chr_22",
                     sumstats_file=sumstats_file)

makedir(osp.dirname(output_f))

if args.model == 'vem_c':
    m = vem_prs(gdl)
elif args.model == 'gibbs_c':
    m = prs_gibbs(gdl)

m.fit()
m.write_inferred_params(output_f)
