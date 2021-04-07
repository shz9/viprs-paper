# Initialization script that sets up the compute environment on ComputeCanada
# You may skip some of these steps if you have a different working environment

module load python/3.7
module load scipy-stack

virtualenv --no-download $SLURM_TMPDIR/env
source $SLURM_TMPDIR/env/bin/activate

cd /home/szabad/projects/def-sgravel/szabad/viprs-paper || exit

pip install --no-index --upgrade pip
pip install --no-index -r requirements.txt

python gwasimulator/setup.py
