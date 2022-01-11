#!/bin/bash
# This is a setup script to prepare the python environment
# for running PRScs.

PRSCS_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Clone the PRScs python repository:
mkdir -p "$PRSCS_PATH/bin/" || exit
git clone https://github.com/getian107/PRScs.git "$PRSCS_PATH/bin/"

# Transform summary statistics:
source external/PRScs/transform_sumstats_job.sh

# Download LD matrix?
