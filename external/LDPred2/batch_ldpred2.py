import glob
import os.path as osp
import argparse
import sys
import os
import subprocess
sys.path.append(osp.dirname(osp.dirname(osp.dirname(__file__))))
from utils import makedir


parser = argparse.ArgumentParser(description='Deploy LDPred2 model fitting jobs on the cluster')

parser.add_argument('-p', '--phenotype', dest='pheno_name', type=str,
                    help='The name of the phenotype.')
parser.add_argument('-c', '--config', dest='config', type=str,
                    help='The simulation configuration on which to perform model fit')
parser.add_argument('-a', '--application', dest='application', type=str,
                    choices={'real', 'simulation'},
                    help='The category of phenotypes to consider')
parser.add_argument('-m', '--model', dest='model', type=str, default='inf',
                    choices={'inf', 'grid', 'auto'})
parser.add_argument('-t', '--type', dest='type', type=str, default='quantitative',
                    choices={'quantitative', 'binary'},
                    help='The type of phenotype to consider')
args = parser.parse_args()

gwas_dir = f"data/gwas/{args.type}"

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
        'Name': f"external/LDPred2-{args.model}/{args.type}/{config}/{trait}"
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

    if args.model == 'inf':
        cmd = ["sbatch", "-J", job['Name'], "--time 04:00:00", "external/LDPred2/ldpred2_job.sh",
               job['Trait'], args.model]
    elif args.model == 'auto':
        cmd = ["sbatch", "-J", job['Name'], "--time 15:00:00", "external/LDPred2/ldpred2_job.sh",
               job['Trait'], args.model]
    else:
        cmd = ["sbatch", "-J", job['Name'], "external/LDPred2/ldpred2_job.sh",
               job['Trait'], args.model]
    print(" ".join(cmd))
    result = subprocess.run(" ".join(cmd), shell=True, capture_output=True)
    print(result.stdout)
