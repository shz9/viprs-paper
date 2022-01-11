#!/bin/bash
# This is a setup script to prepare the R environment
# for running LDPred2.

LDPRED2_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

module load gcc/9.3.0 r/4.0.2
mkdir -p "$LDPRED2_PATH/R_ldpred2_env" || true

export R_LIBS="$LDPRED2_PATH/R_ldpred2_env"

R -e 'install.packages("bigsnpr", repos="https://cloud.r-project.org/")'
R -e 'install.packages("dplyr", repos="https://cloud.r-project.org/")'
