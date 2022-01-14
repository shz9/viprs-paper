#!/bin/bash
# This file contains configurations for running the
# SBayesR model

# LD Panel path
# Downloaded from: https://zenodo.org/record/3350914
LD_PANEL_PATH="$HOME/projects/def-sgravel/data/ld/ukbEURu_hm3_shrunk_sparse"

# MCMC settings:
CHAIN_LENGTH=10000
BURN_IN=2000
OUT_FREQ=100
