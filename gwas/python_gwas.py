import sys
import os.path as osp
import glob
sys.path.append(osp.dirname(osp.dirname(__file__)))
from gwasimulator.GWASDataLoader import GWASDataLoader
from utils import makedir
import argparse

##############################

# Chromosomes used for simulation:

sim_chrs = [22]

parser = argparse.ArgumentParser(description='Perform GWAS')

parser.add_argument('-i', '--input-dir', dest='input_dir', type=str, required=True,
                    help='The input directory with phenotypes as .txt files')
parser.add_argument('-s', '--standardize', dest='standardize', type=bool, default=True,
                    help='Flag whether to standardize the genotype/phenotype or not.')

args = parser.parse_args()

gdl = GWASDataLoader([f"data/ukbb_qc_genotypes/chr_{i}" for i in sim_chrs],
                     compute_ld=False,
                     standardize_genotype=args.standardize)

config_name = osp.basename(args.input_dir)

for pheno_file in glob.glob(osp.join(args.input_dir, "*.txt")):

    pheno_id = osp.basename(pheno_file).replace(".txt", "")
    gdl.read_phenotypes(pheno_file, standardize=args.standardize)

    makedir(f"data/gwas/{config_name}/{pheno_id}/")

    ss_tables = gdl.to_sumstats_table(per_chromosome=True)
    for c, tab in ss_tables.items():
        tab.to_csv(f"data/gwas/{config_name}/{pheno_id}/chr_{c}.PHENO1.glm.linear", index=False, sep="\t")

