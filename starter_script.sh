# Initialization script that sets up the compute environment on ComputeCanada
# You may skip some of these steps if you have a different working environment

cd "$HOME/projects/def-sgravel/szabad/viprs-paper" || exit

source "$HOME/pyenv/bin/activate"

cd gwasimulator || exit
python setup.py

cd "$HOME/projects/def-sgravel/szabad/viprs-paper" || exit
