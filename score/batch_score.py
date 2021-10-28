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
                    choices={'real', 'simulation', 'independent'},
                    help='The category of phenotypes to consider')
parser.add_argument('-t', '--type', dest='type', type=str, default='all',
                    choices={'quantitative', 'binary', 'all'},
                    help='The type of phenotype to consider')
parser.add_argument('-m', '--model', dest='model', type=str, default='all',
                    choices={'VIPRS', 'VIPRSAlpha', 'VIPRSSBayes',
                             'GibbsPRS', 'GibbsPRSSBayes',
                             'VIPRS-BMA', 'VIPRS-BMAl', 'VIPRS-BO', 'VIPRS-BOv',
                             'VIPRS-GS', 'VIPRS-GSl', 'VIPRS-GSv', 'VIPRS-GSvl',
                             'VIPRSAlpha-BMA', 'VIPRSAlpha-BMAl', 'VIPRSAlpha-BO', 'VIPRSAlpha-BOv',
                             'VIPRSAlpha-GS', 'VIPRSAlpha-GSl', 'VIPRSAlpha-GSv', 'VIPRSAlpha-GSvl',
                             'VIPRSSBayes-BMA', 'VIPRSSBayes-BMAl', 'VIPRSSBayes-BO', 'VIPRSSBayes-BOv',
                             'VIPRSSBayes-GS', 'VIPRSSBayes-GSl', 'VIPRSSBayes-GSv', 'VIPRSSBayes-GSvl',
                             'SBayesR',
                             'PRSice2',
                             'LDPred2-inf', 'LDPred2-grid', 'LDPred2-auto',
                             'PRScs',
                             'Lassosum',
                             'all'})
parser.add_argument('-l', '--panel', dest='panel', type=str, default='all',
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

if args.model == 'all':
    model_fit_dir = osp.join(model_fit_dir, "*")
else:
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
    elif args.application == 'independent':
        model_fit_dir = osp.join(model_fit_dir, "independent", "*")
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
