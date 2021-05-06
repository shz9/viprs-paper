"""
Author: Shadi Zabad
Date: May 2021
"""

import sys
import os.path as osp
sys.path.append(osp.dirname(osp.dirname(__file__)))
from gwasimulator.GWASDataLoader import GWASDataLoader
from vemPRS.prs.src.vem_c import vem_prs
from utils import makedir

sumstats_file = sys.argv[1]

output_dir = "data/model_fit/vem_c/"
output_f = osp.join(output_dir, sumstats_file.replace("data/gwas/", '').replace('.PHENO1.glm.linear', '.fit'))

gdl = GWASDataLoader("data/ukbb_qc_genotypes/chr_22.bed",
                     ld_store_files="data/ld/ukbb_windowed/ld_ragged/chr_22",
                     sumstats_file=sumstats_file)

makedir(osp.dirname(output_f))

v = vem_prs(gdl)
v.fit()
v.write_inferred_params(output_f)
