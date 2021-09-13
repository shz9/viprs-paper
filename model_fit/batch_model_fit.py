import glob
import os.path as osp
import argparse
import sys
import os
import subprocess
sys.path.append(osp.dirname(osp.dirname(__file__)))
from utils import makedir


parser = argparse.ArgumentParser(description='Deploy model fitting jobs on the cluster')

parser.add_argument('-p', '--phenotype', dest='pheno_name', type=str,
                    help='The name of the phenotype.')
parser.add_argument('-c', '--config', dest='config', type=str,
                    help='The simulation configuration on which to perform model fit')
parser.add_argument('-a', '--application', dest='application', type=str,
                    choices={'real', 'simulation'},
                    help='The category of phenotypes to consider')
parser.add_argument('--strategy', dest='strategy', type=str, default='EM',
                    choices={'EM', 'BMA', 'BO', 'GS'})
parser.add_argument('-m', '--model', dest='model', type=str, default='VIPRS',
                    choices={'VIPRS', 'VIPRSSBayes', 'GibbsPRS', 'GibbsPRSSBayes'})
parser.add_argument('-l', '--ld-panel', dest='ld_panel', type=str, default='ukbb_50k_windowed',
                    choices={'1000G_sample', '1000G_shrinkage', '1000G_windowed', '1000G_block',
                             'ukbb_1k_sample', 'ukbb_1k_shrinkage', 'ukbb_1k_windowed', 'ukbb_1k_block',
                             'ukbb_10k_sample', 'ukbb_10k_shrinkage', 'ukbb_10k_windowed', 'ukbb_10k_block',
                             'ukbb_50k_sample', 'ukbb_50k_shrinkage', 'ukbb_50k_windowed', 'ukbb_50k_block'})
parser.add_argument('--genomewide', dest='genomewide', action='store_true', default=False,
                    help='Fit all chromosomes jointly')

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


model_name = args.model
if args.strategy != 'EM':
    model_name += f'-{args.strategy}'

if args.genomewide:
    model_name += '-genomewide'

jobs = []

for gd in glob.glob(gwas_dir):

    trait = osp.basename(gd)
    config = osp.basename(osp.dirname(gd))

    jobs.append({
        'Trait': gd,
        'Name': f"{args.ld_panel}/{model_name}/{config}/{trait}",
        'Model': args.model,
        'LD panel': args.ld_panel,
        'Strategy': args.strategy
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

    cmd = ["sbatch", "-J", job['Name']]

    # Time specification:
    if args.strategy in ('BMA', 'GS', 'BO'):
        cmd = ["--time 4:0:0"]
    elif 'sample' in args.ld_panel:
        cmd += ["--time 30:0:0"]

    # Memory specification:
    if args.strategy in ('EM', 'BO') and args.genomewide:
        cmd += ["--mem-per-cpu 3GB"]
    elif args.strategy in ('BMA', 'GS'):
        if args.genomewide:
            cmd += ["--mem-per-cpu 15GB"]
        else:
            cmd += ["--mem-per-cpu 4GB"]
    elif 'sample' in args.ld_panel:
        cmd += ["--mem-per-cpu 10GB"]

    cmd += ["model_fit/model_fit_job.sh",
            job['Trait'], job['Model'], job['LD panel'], job['Strategy']]

    if args.genomewide:
        cmd += ['true']

    print(" ".join(cmd))
    result = subprocess.run(" ".join(cmd), shell=True, capture_output=True)
    print(result.stdout)
