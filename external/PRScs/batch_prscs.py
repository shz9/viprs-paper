import glob
import os.path as osp
import argparse
import sys
import os
import subprocess
sys.path.append(osp.dirname(osp.dirname(osp.dirname(__file__))))
from utils import makedir


parser = argparse.ArgumentParser(description='Deploy PRScs model fitting jobs on the cluster')

parser.add_argument('-p', '--phenotype', dest='pheno_name', type=str,
                    help='The name of the phenotype.')
parser.add_argument('-c', '--config', dest='config', type=str,
                    help='The simulation configuration on which to perform model fit')
parser.add_argument('-a', '--application', dest='application', type=str,
                    choices={'real', 'simulation'},
                    help='The category of phenotypes to consider')
args = parser.parse_args()

gwas_dir = "data/gwas/"

if args.pheno_name is not None:
    gwas_dir = osp.join(gwas_dir, "real_fold_*", args.pheno_name)
elif args.config is not None:
    gwas_dir = osp.join(gwas_dir, args.config, "*")
elif args.application is not None:
    if args.application == 'real':
        gwas_dir = osp.join(gwas_dir, "real_fold_*", "*")
    else:
        gwas_dir = osp.join(gwas_dir, "h2_*", "*")
else:
    gwas_dir = osp.join(gwas_dir, "*", "*")

jobs = []

for gd in glob.glob(gwas_dir):

    trait = osp.basename(gd)
    config = osp.basename(osp.dirname(gd))

    jobs.append({
        'Trait': gd,
        'Name': f"external/PRScs/{config}/{trait}"
    })

if len(jobs) > 500:
    print("Cannot submit more than 500 jobs simultaneously. Please re-run with specific arguments.")
    sys.exit()

for job in jobs:

    makedir(osp.dirname(f"./log/model_fit/{job['Name']}.out"))

    try:
        os.remove(f"./log/model_fit/{job['Name']}.out")
    except Exception as e:
        pass

    cmd = ["sbatch", "-J", job['Name'], "external/PRScs/fit_prscs.sh", job['Trait']]
    print(" ".join(cmd))
    result = subprocess.run(" ".join(cmd), shell=True, capture_output=True)
    print(result.stdout)
