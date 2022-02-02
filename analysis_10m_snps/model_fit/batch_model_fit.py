import glob
import os.path as osp
import argparse
import sys
import os
import subprocess
sys.path.append(osp.dirname(osp.dirname(osp.dirname(__file__))))
from utils import makedir


parser = argparse.ArgumentParser(description='Deploy model fitting jobs on the cluster')

parser.add_argument('-p', '--phenotype', dest='pheno_name', type=str,
                    help='The name of the phenotype.')
parser.add_argument('-c', '--config', dest='config', type=str,
                    help='The simulation configuration on which to perform model fit')
parser.add_argument('-a', '--application', dest='application', type=str,
                    choices={'real', 'simulation'},
                    help='The category of phenotypes to consider')
parser.add_argument('-t', '--type', dest='type', type=str, default='all',
                    choices={'quantitative', 'binary', 'all'},
                    help='The type of phenotype to consider')
parser.add_argument('--strategy', dest='strategy', type=str, default='EM',
                    choices={'EM', 'BMA', 'BO', 'GS'})
parser.add_argument('-m', '--model', dest='model', type=str, default='VIPRS',
                    choices={'VIPRS', 'VIPRSMix', 'VIPRSAlpha', 'VIPRSSBayes', 'VIPRSMixSBayes',
                             'VIPRSSBayesAlpha', 'GibbsPRS', 'GibbsPRSSBayes'})
parser.add_argument('-l', '--ld-panel', dest='ld_panel', type=str, default='ukbb_all_windowed',
                    choices={'1000G_sample', '1000G_shrinkage', '1000G_windowed', '1000G_block',
                             'ukbb_1k_sample', 'ukbb_1k_shrinkage', 'ukbb_1k_windowed', 'ukbb_1k_block',
                             'ukbb_10k_sample', 'ukbb_10k_shrinkage', 'ukbb_10k_windowed', 'ukbb_10k_block',
                             'ukbb_50k_sample', 'ukbb_50k_shrinkage', 'ukbb_50k_windowed', 'ukbb_50k_block',
                             'ukbb_all_windowed'})
parser.add_argument('--skip-completed', dest='skip_completed', action='store_true', default=False,
                    help='Skip runs that have been completed before.')

args = parser.parse_args()

if args.type == 'all':
    gwas_dir = f"data_all/gwas/*"
else:
    gwas_dir = f"data_all/gwas/{args.type}"

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

if args.strategy in ('GS', 'BO') and args.grid_metric == 'validation':
    model_name += 'v'

if args.strategy in ('GS', 'BMA') and args.localgrid:
    model_name += 'l'


jobs = []

for gd in glob.glob(gwas_dir):

    trait = osp.basename(gd)
    config = osp.basename(osp.dirname(gd))
    trait_type = osp.basename(osp.dirname(osp.dirname(gd)))

    for chrom in range(1, 23):

        if args.skip_completed:
            if osp.isfile(f"data_all/model_fit/{args.ld_panel}/{model_name}/{trait_type}/{config}/{trait}/chr_{chrom}.fit"):
                continue

        jobs.append({
            'Trait': gd,
            'Name': f"{args.ld_panel}/{model_name}/{trait_type}/{config}/{trait}/chr_{chrom}",
            'Model': args.model,
            'LD panel': args.ld_panel,
            'Strategy': args.strategy,
            'Chromosome': str(chrom)
        })

if len(jobs) > 1000:
    print("Cannot submit more than 1000 jobs simultaneously. Please re-run with specific arguments.")
    sys.exit()

for job in jobs:

    makedir(osp.dirname(f"./log_all/model_fit/{job['Name']}.out"))

    try:
        os.remove(f"./log_all/model_fit/{job['Name']}.out")
    except Exception as e:
        pass

    cmd = ["sbatch", "-J", job['Name']]

    cmd += ["analysis_10m_snps/model_fit/model_fit_job.sh",
            job['Trait'], job['Model'], job['LD panel'], job['Strategy'], job['Chromosome']]

    print(" ".join(cmd))
    result = subprocess.run(" ".join(cmd), shell=True, capture_output=True)
    print(result.stdout)

