"""
Author: Shadi Zabad
Date: April 2021
"""

import sys
import os.path as osp
sys.path.append(osp.dirname(osp.dirname(__file__)))
from gwasimulator.GWASSimulator import GWASSimulator
from utils import makedir

# --------- Options ---------

output_dir = "data/simulated_phenotypes"

h2g = [0.1, 0.3, 0.5]  # Heritability
prop_causal = [0.1, 0.01, 0.001]  # Proportion of causal variants
n_phenotypes = 100  # Number of phenotypes to simulate per configuration
sim_chrs = [22]  # Chromosomes used for simulation

# ---------------------------

gs = GWASSimulator([f"data/ukbb_qc_genotypes/chr_{i}" for i in sim_chrs],
                   compute_ld=False)

for h2 in h2g:

    for pc in prop_causal:

        sub_dir = osp.join(output_dir, f'h2_{h2}_p_{pc}')

        makedir(sub_dir)

        gs.h2g = h2
        gs.pis = (1. - pc, pc)

        for i in range(n_phenotypes):
            gs.simulate(reset_betas=True, perform_gwas=False)

            pheno_table = gs.to_phenotype_table()
            pheno_table.to_csv(osp.join(sub_dir, str(i + 1) + '.txt'), sep="\t", index=False, header=False)
