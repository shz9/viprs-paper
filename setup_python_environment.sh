#!/bin/bash
# This script creates the python environment for running the VIPRS model
# on a compute node.

module load python/3.7
virtualenv --no-download $SLURM_TMPDIR/env
source $SLURM_TMPDIR/env/bin/activate
pip install --no-index --upgrade pip

pip install --no-index -r gwasimulator/requirements.txt
pip install --no-index -r vemPRS/requirements.txt

