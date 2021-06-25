import sys
import os.path as osp
sys.path.append(osp.dirname(osp.dirname(__file__)))
from gwasimulator.GWASDataLoader import GWASDataLoader
from utils import makedir
import argparse
import functools
print = functools.partial(print, flush=True)

##############################

# Chromosomes used for simulation:

parser = argparse.ArgumentParser(description='Perform GWAS')

parser.add_argument('-c', '--chromosome', dest='chromosome', type=str, default=22,
                    help='The chromosome number to use for the regression')
parser.add_argument('-p', '--pheno-file', dest='pheno_file', type=str, required=True,
                    help='The input phenotype file with tab delimited entries.')
parser.add_argument('-s', '--standardize', dest='standardize', type=bool, default=True,
                    help='Flag whether to standardize the genotype/phenotype or not.')

args = parser.parse_args()

print(f"> Generating GWAS summary statistics for {args.pheno_file}", flush=True)

gdl = GWASDataLoader(f"data/ukbb_qc_genotypes/chr_{args.chromosome}",
                     keep_individuals="data/keep_files/ukbb_train_subset.keep",
                     compute_ld=False,
                     standardize_genotype=args.standardize,
                     phenotype_file=args.pheno_file,
                     standardize_phenotype=args.standardize)

config_name = osp.basename(osp.dirname(args.pheno_file))
pheno_id = osp.basename(args.pheno_file).replace(".txt", "")

makedir(f"data/gwas/{config_name}/{pheno_id}/")

print(f"> Saving the results to: data/gwas/{config_name}/{pheno_id}/", flush=True)

ss_tables = gdl.to_sumstats_table(per_chromosome=True)
for c, tab in ss_tables.items():
    tab.to_csv(f"data/gwas/{config_name}/{pheno_id}/chr_{c}.PHENO1.glm.linear", index=False, sep="\t")

