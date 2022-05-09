#!/bin/bash
# Initialization script that sets up the compute environment on ComputeCanada
# You may skip some of these steps if you have a different working environment

VIPRS_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd "$VIPRS_PATH" || exit

# Create a python virtual environment `pyenv`
module load python/3.7
python -m venv "$HOME/pyenv"

source "$HOME/pyenv/bin/activate"

# Upgrade pip:
pip install --upgrade pip

# Install requirements for viprs-paper:
pip install -r requirements.txt
# Install requirements for magenpy:
pip install -r magenpy/requirements.txt
# Install optional requirements for magenpy:
pip install -r magenpy/optional-requirements.txt
# Install requirements for viprs:
pip install -r viprs/requirements.txt
# Install optional requirements for viprs:
pip install -r viprs/optional-requirements.txt

# Compile the Cython code for magenpy:
cd magenpy || exit
python setup.py

# Compile the Cython code for viprs:
cd ../viprs || exit
python setup.py

# Compile the Cython code for magenpy (within viprs):
cd prs/magenpy || exit
python setup.py

cd "$VIPRS_PATH" || exit
