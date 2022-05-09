"""
Author: Shadi Zabad
Date: April 2021
"""

import sys
import os
import os.path as osp
sys.path.append(osp.dirname(osp.dirname(__file__)))
from magenpy.GWASSimulator import GWASSimulator
from utils import makedir
import argparse
import functools
print = functools.partial(print, flush=True)

# --------- Options ---------

parser = argparse.ArgumentParser(description='A module for simulating phenotypes')

parser.add_argument('--h2g', dest='h2g', type=float, default=0.1,
                    help='Trait heritability (0. - 1.)')
parser.add_argument('-p', dest='prop_causal', type=float, default=0.01,
                    help='Proportion of causal SNPs (0. - 1.)')
parser.add_argument('-r', dest='replicate', type=int, default=1,
                    help='replicate number')
parser.add_argument('-t', dest='type', type=str, default='quantitative',
                    choices={'quantitative', 'binary'},
                    help='Type of phenotype')

args = parser.parse_args()


h2 = args.h2g
pc = args.prop_causal
output_dir = f"data/phenotypes/{args.type}"
sim_chrs = range(1, 23)  # Chromosomes used for simulation

# ---------------------------

gs = GWASSimulator([f"data/ukbb_qc_genotypes/chr_{i}" for i in sim_chrs],
                   phenotype_likelihood=['gaussian', 'binomial'][args.type == 'binary'],
                   compute_ld=False,
                   use_plink=True,
                   temp_dir=os.getenv('SLURM_TMPDIR', 'temp'))

sub_dir = osp.join(output_dir, f'h2_{h2}_p_{pc}')

makedir(sub_dir)

gs.h2g = h2
gs.pis = (1. - pc, pc)

print(f"> Simulating phenotype (replicate {args.replicate}...")
gs.simulate(reset_beta=True, perform_gwas=False)

pheno_table = gs.to_phenotype_table()
pheno_table.to_csv(osp.join(sub_dir, f'{args.replicate}.txt'), sep="\t", index=False, header=False)
