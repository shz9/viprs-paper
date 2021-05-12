"""
Author: Shadi Zabad
Date: May 2021
"""

import sys
import os.path as osp
sys.path.append(osp.dirname(osp.dirname(__file__)))
from gwasimulator.GWASDataLoader import GWASDataLoader
from utils import makedir
import argparse


sim_chrs = [22]  # Chromosomes used for simulation

test_data = GWASDataLoader([f"data/ukbb_qc_genotypes/chr_{i}" for i in sim_chrs],
                           keep_individuals="data/keep_files/ukbb_test_subset.keep",
                           compute_ld=False)
