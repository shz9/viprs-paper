import argparse
import glob
import os
import os.path as osp
import sys
sys.path.append(osp.dirname(osp.dirname(__file__)))
from utils import makedir
import subprocess

parser = argparse.ArgumentParser(description='Deploy GWAS jobs on the cluster')

parser.add_argument('-p', '--phenotype', dest='pheno_name', type=str,
                    help='The name of the phenotype.')
parser.add_argument('-c', '--config', dest='config', type=str,
                    help='The simulation configuration on which to perform GWAS')
parser.add_argument('-s', '--software', dest='software', type=str, default='plink',
                    choices={'plink', 'python'},
                    help='The software to use to perform GWAS')
parser.add_argument('-a', '--application', dest='application', type=str,
                    choices={'real', 'simulation'},
                    help='The category of phenotypes to consider')
parser.add_argument('-t', '--type', dest='type', type=str, default='quantitative',
                    choices={'quantitative', 'binary'},
                    help='The type of phenotype to consider')

args = parser.parse_args()

pheno_dir = f"data/phenotypes/{args.type}"
keepfile_dir = "data/keep_files"

if args.pheno_name is not None:
    pheno_dir = osp.join(pheno_dir, "real", args.pheno_name + ".txt")
elif args.config is not None:
    pheno_dir = osp.join(pheno_dir, args.config, "*.txt")
elif args.application is not None:
    if args.application == 'real':
        pheno_dir = osp.join(pheno_dir, "real", "*.txt")
    else:
        pheno_dir = osp.join(pheno_dir, "h2_*", "*.txt")
else:
    pheno_dir = osp.join(pheno_dir, "*", "*.txt")

jobs = []

for trait_f in glob.glob(pheno_dir):

    trait = osp.basename(trait_f).replace('.txt', '')
    config = osp.basename(osp.dirname(trait_f))

    if config == 'real':
        for keep_f in glob.glob(osp.join(keepfile_dir, 'ukbb_cv', trait, "*/train.keep")):
            fold = osp.basename(osp.dirname(keep_f))
            jobs.append({
                'Trait': trait_f,
                'Keep': keep_f,
                'Name': f"{args.software}/{args.type}/{config}_{fold}/{trait}",
                'Output': f"data/gwas/{args.type}/{config}_{fold}/{trait}"
            })
    else:
        jobs.append({
            'Trait': trait_f,
            'Keep': osp.join(keepfile_dir, "ukbb_train_subset.keep"),
            'Name': f"{args.software}/{args.type}/{config}/{trait}",
            'Output': f"data/gwas/{args.type}/{config}/{trait}"
        })

if len(jobs) > 500:
    print("Cannot submit more than 500 jobs simultaneously. Please re-run with specific arguments.")
    sys.exit()

for job in jobs:

    makedir(osp.dirname(f"./log/gwas/{job['Name']}.out"))

    try:
        os.remove(f"./log/gwas/{job['Name']}.out")
    except Exception as e:
        pass

    cmd = ["sbatch", "-J", job['Name'], f"gwas/gwas_{args.software}_job.sh", job['Trait'], job['Keep'], job['Output']]
    print(" ".join(cmd))
    result = subprocess.run(" ".join(cmd), shell=True, capture_output=True)
    print(result.stdout)
