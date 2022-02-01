import glob
import os.path as osp
import sys
import os
import argparse
import subprocess
sys.path.append(osp.dirname(osp.dirname(__file__)))
from utils import makedir


parser = argparse.ArgumentParser(description='Deploy scoring jobs on the cluster')

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
parser.add_argument('-m', '--model', dest='model', type=str, required=True)
parser.add_argument('-l', '--panel', dest='panel', type=str, default='ukbb_50k_windowed',
                    choices={'external', '1000G_sample', '1000G_shrinkage', '1000G_windowed', '1000G_block',
                             'ukbb_1k_sample', 'ukbb_1k_shrinkage', 'ukbb_1k_windowed', 'ukbb_1k_block',
                             'ukbb_10k_sample', 'ukbb_10k_shrinkage', 'ukbb_10k_windowed', 'ukbb_10k_block',
                             'ukbb_50k_sample', 'ukbb_50k_shrinkage', 'ukbb_50k_windowed', 'ukbb_50k_block',
                             'all'})

args = parser.parse_args()

model_fit_dir = "data/model_fit/"

if args.panel == 'all':
    model_fit_dir = osp.join(model_fit_dir, "*")
else:
    model_fit_dir = osp.join(model_fit_dir, args.panel)

model_fit_dir = osp.join(model_fit_dir, args.model)

if args.type == 'all':
    model_fit_dir = osp.join(model_fit_dir, "*")
else:
    model_fit_dir = osp.join(model_fit_dir, args.type)

if args.pheno_name is not None:
    model_fit_dir = osp.join(model_fit_dir, "real_fold_*", args.pheno_name)
elif args.config is not None:
    model_fit_dir = osp.join(model_fit_dir, args.config, "*")
elif args.application is not None:
    if args.application == 'real':
        model_fit_dir = osp.join(model_fit_dir, "real_fold_*", "*")
    else:
        model_fit_dir = osp.join(model_fit_dir, "h2_*", "*")
else:
    model_fit_dir = osp.join(model_fit_dir, "*", "*")


jobs = []

for mdir in glob.glob(model_fit_dir):

    jobs.append({
        'Trait': mdir,
        'Name': mdir.replace('data/model_fit/', '')
    })

if len(jobs) < 1:
    raise Exception("No model fits were found with the required characteristics:", model_fit_dir)

for job in jobs:

    makedir(osp.dirname(f"./log/score/{job['Name']}.out"))

    try:
        os.remove(f"./log/score/{job['Name']}.out")
    except Exception as e:
        pass

    cmd = ["sbatch", "-J", job['Name'], "score/score_job.sh", job['Trait']]
    print(" ".join(cmd))
    result = subprocess.run(" ".join(cmd), shell=True, capture_output=True)
    print(result.stdout)
