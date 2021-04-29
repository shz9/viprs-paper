"""
Author: Shadi Zabad
Date: April 2021
"""

import sys
import os.path as osp
sys.path.append(osp.dirname(osp.dirname(__file__)))
from gwasimulator.GWASSimulator import GWASSimulator
from utils import makedir
import argparse

# --------- Options ---------

parser = argparse.ArgumentParser(description='A module for simulating phenotypes')

parser.add_argument('-h', '--h2g', dest='h2g', type=float, default=0.1,
                    help='Trait heritability (0. - 1.)')
parser.add_argument('-p', '--pc', dest='prop_causal', type=float, default=0.01,
                    help='Proportion of causal SNPs (0. - 1.)')
parser.add_argument('-n', '--replicates', dest='n_replicates', type=int, default=10,
                    help='Number of replicates')

args = parser.parse_args()


h2 = args.h2g
pc = args.prop_causal
output_dir = "data/simulated_phenotypes"
sim_chrs = [22]  # Chromosomes used for simulation

# ---------------------------

gs = GWASSimulator([f"data/ukbb_qc_genotypes/chr_{i}" for i in sim_chrs],
                   compute_ld=False)

sub_dir = osp.join(output_dir, f'h2_{h2}_p_{pc}')

makedir(sub_dir)

gs.h2g = h2
gs.pis = (1. - pc, pc)

for i in range(args.n_replicates):
    gs.simulate(reset_beta=True, perform_gwas=False)

    pheno_table = gs.to_phenotype_table()
    pheno_table.to_csv(osp.join(sub_dir, str(i + 1) + '.txt'), sep="\t", index=False, header=False)
