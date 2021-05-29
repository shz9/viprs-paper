"""
Author: Shadi Zabad
Date: May 2021
"""

import sys
import os.path as osp
import glob
import pandas as pd
sys.path.append(osp.dirname(osp.dirname(__file__)))
sys.path.append("vemPRS/")
from gwasimulator.GWASDataLoader import GWASDataLoader
from vemPRS.prs.src.PRSModel import PRSModel
from scipy import stats
from utils import makedir
import argparse


def evaluate_predictive_performance(true_phenotype, pred_phenotype):

    _, _, r_val, _, _ = stats.linregress(pred_phenotype, true_phenotype)

    return {
        'R2': r_val**2
    }

parser = argparse.ArgumentParser(description='Evaluate PRS models')

parser.add_argument('-p', '--phenotype-file', dest='phenotype_file', type=str, required=True,
                    help='The file with the parameter fits')
parser.add_argument('-l', '--ld-panel', dest='ld_panel', type=str, required=True,
                    help='The LD panel that was used for model fit')
args = parser.parse_args()

phenotype_file = args.phenotype_file
config, trait = phenotype_file.split("/")[-2:]
trait = trait.replace('.txt', '')

output_file = f"data/evaluation/{args.ld_panel}/{config}/{trait}.csv"

sim_chrs = [22]  # Chromosomes used for simulation

test_data = GWASDataLoader([f"data/ukbb_qc_genotypes/chr_{i}" for i in sim_chrs],
                           keep_individuals="data/keep_files/ukbb_test_subset.keep",
                           phenotype_file=phenotype_file,
                           compute_ld=False)
prs_m = PRSModel(test_data)

dfs = []

for fit_file in glob.glob(f"data/model_fit/{args.ld_panel}/*/{config}/{trait}/chr_22.fit"):
    prs_m.read_inferred_params(fit_file)

    pred_perf = evaluate_predictive_performance(test_data.phenotypes,
                                                prs_m.predict_phenotype())
    pred_perf.update({'Trait': trait, 'Model': fit_file.split("/")[3]})

    dfs.append(pd.DataFrame.from_dict(pred_perf, orient='index').T)

makedir(osp.dirname(output_file))
pd.concat(dfs).to_csv(output_file)
