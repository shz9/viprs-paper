import sys
import os
import os.path as osp
sys.path.append(osp.dirname(osp.dirname(osp.dirname(__file__))))
import argparse
from gwasimulator.GWASDataLoader import GWASDataLoader

parser = argparse.ArgumentParser(description='Computing LD matrices')
parser.add_argument('-c', '--chromosome', dest='chrom', type=str, required=True)
args = parser.parse_args()


gdl = GWASDataLoader(f"data_all/ukbb_qc_genotypes/chr_{args.chrom}",
                     ld_estimator="windowed",
                     window_unit="cM",
                     cm_window_cutoff=3.,
                     min_mac=5,
                     min_maf=0.001,
                     use_plink=True,
                     compute_ld=True,
                     output_dir=f"data_all/ld/ukbb_all_windowed/",
                     temp_dir="/home/szabad/projects/ctb-sgravel/szabad/temp/",
                     n_threads=15)

gdl.cleanup()
