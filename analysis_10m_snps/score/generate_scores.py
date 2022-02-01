"""
Author: Shadi Zabad
Date: May 2021
"""

import sys
import os
import os.path as osp
import glob
sys.path.append(osp.dirname(osp.dirname(osp.dirname(__file__))))
sys.path.append("viprs/")
from gwasimulator.GWASDataLoader import GWASDataLoader
from viprs.prs.src.PRSModel import PRSModel
from utils import makedir
import argparse
import functools
print = functools.partial(print, flush=True)


parser = argparse.ArgumentParser(description='Generate Polygenic Scores')

parser.add_argument('-f', '--fit-dir', dest='fit_dir', type=str, required=True,
                    help='The directory with the outputted parameter fits')
args = parser.parse_args()

fit_dir = osp.normpath(args.fit_dir)
trait = osp.basename(fit_dir)
config_dir = osp.dirname(fit_dir)
config = osp.basename(config_dir)
trait_type = osp.basename(osp.dirname(config_dir))

if 'real' in config:
    keep_file = f"data/keep_files/ukbb_cv/{trait_type}/{trait}/{config.replace('real_', '')}/test.keep"
else:
    keep_file = "data/keep_files/ukbb_test_subset.keep"

test_data = GWASDataLoader([f"data_all/ukbb_qc_genotypes/chr_{chrom}.bed" for chrom in range(1, 23)],
                           keep_individuals=keep_file,
                           min_mac=None,
                           min_maf=None,
                           use_plink=True,
                           compute_ld=False,
                           temp_dir=os.getenv('SLURM_TMPDIR', 'temp'))
prs_m = PRSModel(test_data)
prs_m.read_inferred_params(glob.glob(osp.join(fit_dir, "*.fit")))

# Predict on the test set:
print("> Generating polygenic scores...")
prs = test_data.score_plink(prs_m.inf_beta)

print("> Saving results...")
# Save the PRS for this chromosome as a table:

ind_table = test_data.to_individual_table()
ind_table['PRS'] = prs

# Clean up all the intermediate files/directories
test_data.cleanup()

# Output the scores:
output_f = fit_dir.replace("model_fit", "test_scores") + '.prs'
makedir(osp.dirname(output_f))
ind_table.to_csv(output_f, index=False, sep="\t")
