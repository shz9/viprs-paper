"""
Author: Shadi Zabad
Date: April 2021
"""

from gwasimulator.GWASDataLoader import GWASDataLoader

GWASDataLoader("data/ukbb_qc_genotypes/chr_",
               ld_subset_samples="data/keep_files/ukbb_ld_subset.keep",
               ld_estimator="windowed",
               window_unit="cM",
               cm_window_cutoff=1.,
               compute_ld=True,
               sparse_ld=True,
               temp_dir="data/ld/ukbb_windowed/")

GWASDataLoader("data/ukbb_qc_genotypes/chr_",
               ld_subset_samples="data/keep_files/ukbb_ld_subset.keep",
               ld_estimator="shrinkage",
               genmap_Ne=11400,
               genmap_sample_size=183,
               shrinkage_cutoff=1e-3,
               compute_ld=True,
               sparse_ld=True,
               temp_dir="data/ld/ukbb_shrinkage/")
