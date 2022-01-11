#!/bin/bash
# This is a setup script to prepare the R environment
# for running Lassosum.

LASSOSUM_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

module load gcc/9.3.0 r/4.0.2
mkdir -p "$LASSOSUM_PATH/R_lassosum_env" || true

export R_LIBS="$LASSOSUM_PATH/R_lassosum_env"

R -e 'install.packages("remotes", repos="https://cloud.r-project.org/")'
R -e 'remotes::install_github("tshmak/lassosum")'
