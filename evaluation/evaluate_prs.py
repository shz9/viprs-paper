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
import functools
print = functools.partial(print, flush=True)


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

# Find the fir files corresponding to unique chromosomes:
unique_chroms = [osp.basename(f).replace(".fit", "")
                 for f in glob.glob(f"data/model_fit/{args.ld_panel}/*/{config}/{trait}/*.fit")]


test_data = GWASDataLoader([f"data/ukbb_qc_genotypes/{i}" for i in unique_chroms],
                           keep_individuals="data/keep_files/ukbb_test_subset.keep",
                           phenotype_file=phenotype_file,
                           compute_ld=False)
prs_m = PRSModel(test_data)

dfs = []

print(f"Evaluating PRS models in the directory: data/model_fit/{args.ld_panel}/")

for model_dir in glob.glob(f"data/model_fit/{args.ld_panel}/*/"):

    model = osp.basename(model_dir)  # Get the model name
    model_fit_files = glob.glob(osp.join(model_dir, f"{config}/{trait}/*.fit"))

    print(f"> Evaluating model: {model}")

    # Check that all required chromosomes have been fit under this model:
    if any([osp.basename(mff).replace(".fit", "") not in unique_chroms for mff in model_fit_files]):
        print(f"Model {model} does not have parameter fits for all chromosomes. Skipping evaluation...")
        continue

    # Read the inferred parameters:
    prs_m.read_inferred_params(model_fit_files)

    # Evaluate predictive performance:
    pred_perf = evaluate_predictive_performance(test_data.phenotypes,
                                                prs_m.predict())
    pred_perf.update({'Trait': trait, 'Model': model})

    # Append to the results table:
    dfs.append(pd.DataFrame.from_dict(pred_perf, orient='index').T)

makedir(osp.dirname(output_file))
pd.concat(dfs).to_csv(output_file)
