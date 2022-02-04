"""
Author: Shadi Zabad
Date: May 2021
"""

import sys
import os
import os.path as osp
import glob
import numpy as np
import pandas as pd
sys.path.append(osp.dirname(osp.dirname(osp.dirname(__file__))))
sys.path.append("viprs/")
from gwasimulator.GWASDataLoader import GWASDataLoader
from viprs.prs.src.VIPRS import VIPRS
from viprs.prs.src.VIPRSMix import VIPRSMix
from viprs.prs.src.VIPRSAlpha import VIPRSAlpha
from viprs.prs.src.VIPRSSBayes import VIPRSSBayes
from viprs.prs.src.VIPRSMixSBayes import VIPRSMixSBayes
from viprs.prs.src.VIPRSSBayesAlpha import VIPRSSBayesAlpha
from viprs.prs.src.GibbsPRS import GibbsPRS
from viprs.prs.src.GibbsPRSSBayes import GibbsPRSSBayes
from viprs.prs.src.HyperparameterSearch import BMA, GridSearch, BayesOpt
from utils import makedir
import argparse
import functools
print = functools.partial(print, flush=True)


def main():

    parser = argparse.ArgumentParser(description='Fit PRS models')

    parser.add_argument('--chromosome', dest='chrom', type=int,
                        help='Perform model fitting using the provided chromosome only.')
    parser.add_argument('-m', '--model', dest='model', type=str, default='VIPRS',
                        help='The PRS model to fit',
                        choices={'VIPRS', 'VIPRSMix', 'VIPRSAlpha', 'VIPRSSBayes', 'VIPRSMixSBayes',
                                 'VIPRSSBayesAlpha', 'GibbsPRS', 'GibbsPRSSBayes'})
    parser.add_argument('-f', '--fitting-strategy', dest='fitting_strategy', type=str, default='EM',
                        help='The strategy for fitting the hyperparameters', choices={'EM', 'BO', 'GS', 'BMA'})
    parser.add_argument('-l', '--ld-panel', dest='ld_panel', type=str, default='ukbb_all_windowed',
                        help='The LD panel to use in model fit')
    parser.add_argument('-s', '--sumstats', dest='ss_dir', type=str, required=True,
                        help='The summary statistics directory')
    parser.add_argument('--genomewide', dest='genomewide', action='store_true', default=False,
                        help='Fit all chromosomes jointly')
    parser.add_argument('--grid-metric', dest='grid_metric', type=str, default='ELBO',
                        help='The metric for selecting best performing model in grid search',
                        choices={'ELBO', 'validation'})
    parser.add_argument('--local-grid', dest='localgrid', action='store_true', default=False,
                        help='Whether to use localized grid in GS/BMA')
    parser.add_argument('--opt-params', dest='opt_params', type=str,
                        default='sigma_epsilon,pi',
                        help='The hyperparameters to optimize using GridSearch/BMA/Bayesian optimization')

    args = parser.parse_args()

    ss_dir = osp.normpath(args.ss_dir)  # Get the summary statistics directory
    trait_type = osp.basename(osp.dirname(osp.dirname(ss_dir)))
    config = osp.basename(osp.dirname(ss_dir))
    trait = osp.basename(ss_dir)
    opt_params = args.opt_params.split(',')

    print("> Processing GWAS summary statistics in:", ss_dir)
    print("> Loading the LD data and associated summary statistics file...")

    sumstats_format = 'plink'
    ss_files = sorted(glob.glob(osp.join(ss_dir, "*.PHENO1.glm.*")),
                      key=lambda x: int(osp.basename(x).split('.')[0].split('_')[1]))
    if args.chrom is not None:
        ss_files = [ssf for ssf in ss_files if f'chr_{args.chrom}.' in ssf]
    ld_panel_files = [f"data_all/ld/{args.ld_panel}/ld/{osp.basename(ssf).split('.')[0]}" for ssf in ss_files]


    file_sets = []

    if args.genomewide:
        file_sets.append({
            'LD': ld_panel_files,
            'SS': ss_files
        })
    else:
        for ldf, ssf in zip(ld_panel_files, ss_files):
            file_sets.append({
                'LD': ldf,
                'SS': ssf
            })

    if args.fitting_strategy == 'EM':
        output_dir = f"data_all/model_fit/{args.ld_panel}/{args.model}"
    else:
        output_dir = f"data_all/model_fit/{args.ld_panel}/{args.model}-{args.fitting_strategy}"

    if args.fitting_strategy in ('GS', 'BO') and args.grid_metric == 'validation':
        output_dir += "v"

    if args.fitting_strategy in ('GS', 'BMA') and args.localgrid:
        output_dir += "l"

    if args.fitting_strategy in ('BMA', 'GS', 'BO'):
        output_dir += '_'
        for p in sorted(opt_params):
            if p == 'sigma_epsilon':
                output_dir += 'e'
            elif p == 'sigma_beta':
                output_dir += 'b'
            elif p == 'pi':
                output_dir += 'p'
            elif p == 'alpha':
                output_dir += 'a'

    if args.genomewide:
        output_dir = osp.join(output_dir + "-genomewide", trait_type, config, trait)
    else:
        output_dir = osp.join(output_dir, trait_type, config, trait)

    print("> Storing model fit results in:", output_dir)
    makedir(output_dir)

    # Options to provide to the VIPRS objects:
    run_opts = {}

    if args.fitting_strategy in ('BMA', 'GS', 'BO'):
        max_iter = 300
        if args.fitting_strategy in ('BMA', 'GS'):
            if len(opt_params) == 1:
                for p in opt_params:
                    run_opts = {p + '_steps': 30}
            elif len(opt_params) == 2 and 'alpha' in opt_params:
                for p in opt_params:
                    if p != 'alpha':
                        run_opts = {p + '_steps': 20}
    elif 'sample' in args.ld_panel:
        max_iter = 300
    else:
        max_iter = 300

    h2g = []
    prop_causal = []

    for fs in file_sets:

        print("- - - - - - - - - - - - - - - - - - - -")

        gdl = GWASDataLoader(ld_store_files=fs['LD'],
                             sumstats_files=fs['SS'],
                             sumstats_format=sumstats_format,
                             temp_dir=os.getenv('SLURM_TMPDIR', 'temp'))

        if args.fitting_strategy in ('GS', 'BO') and args.grid_metric == 'validation':

            print("> Reading validation dataset...")

            if 'real' in config:
                validation_keep = f"data/keep_files/ukbb_cv/{trait_type}/{trait}/{config.replace('real_', '')}/validation.keep"
            else:
                validation_keep = "data/keep_files/ukbb_valid_subset.keep"

            if 'real' in config:
                phenotype_file = f"data/phenotypes/{trait_type}/real/{trait}.txt"
            else:
                phenotype_file = f"data/phenotypes/{trait_type}/{config}/{trait}.txt"

            validation_gdl = GWASDataLoader(bed_files=[f"data_all/ukbb_qc_genotypes/chr_{chrom}.bed"
                                                       for chrom in gdl.chromosomes],
                                            keep_individuals=validation_keep,
                                            phenotype_likelihood=['gaussian', 'binomial'][trait_type == 'binary'],
                                            phenotype_file=phenotype_file,
                                            compute_ld=False,
                                            use_plink=True,
                                            temp_dir=os.getenv('SLURM_TMPDIR', 'temp'))
        else:
            validation_gdl = None

        if args.model == 'VIPRS':
            prs_m = VIPRS(gdl)
        elif args.model == 'VIPRSMix':
            prs_m = VIPRSMix(gdl, K=3, prior_multipliers=[0.01, 0.1, 1.])
        elif args.model == 'VIPRSAlpha':
            prs_m = VIPRSAlpha(gdl)
        elif args.model == 'VIPRSSBayes':
            prs_m = VIPRSSBayes(gdl)
        elif args.model == 'VIPRSMixSBayes':
            prs_m = VIPRSMixSBayes(gdl, K=3, prior_multipliers=[0.01, 0.1, 1.])
        elif args.model == 'VIPRSSBayesAlpha':
            prs_m = VIPRSSBayesAlpha(gdl)
        elif args.model == 'GibbsPRS':
            prs_m = GibbsPRS(gdl)
        elif args.model == 'GibbsPRSSBayes':
            prs_m = GibbsPRSSBayes(gdl)

        # Fit the model to the data:
        if args.genomewide:
            print("> Performing model fit on all chromosomes jointly...")
        else:
            print("> Performing model fit on chromosome:", gdl.chromosomes)

        try:
            if args.fitting_strategy == 'BO':
                hs_m = BayesOpt(gdl,
                                prs_m,
                                opt_params=opt_params,
                                validation_gdl=validation_gdl,
                                objective=args.grid_metric)
            elif args.fitting_strategy == 'GS':
                hs_m = GridSearch(gdl,
                                  prs_m,
                                  opt_params=opt_params,
                                  validation_gdl=validation_gdl,
                                  objective=args.grid_metric,
                                  localized_grid=args.localgrid,
                                  n_jobs=7)
            elif args.fitting_strategy == 'BMA':
                hs_m = BMA(gdl,
                           prs_m,
                           opt_params=opt_params,
                           localized_grid=args.localgrid,
                           n_jobs=7)
            else:
                hs_m = prs_m

            final_m = hs_m.fit(max_iter=max_iter, **run_opts)
        except Exception as e:
            print(e)
            raise e

        print("> Writing out the inference results...")

        # Write inferred model parameters:
        final_m.write_inferred_params(output_dir, per_chromosome=True)

        # Write the estimated hyperparameters:

        m_h2g = final_m.get_heritability()
        m_p = final_m.get_proportion_causal()

        if not args.genomewide and args.fitting_strategy != 'BMA':

            # Write the per-chromosome estimates:
            chrom = gdl.chromosomes[0]
            final_m.write_inferred_theta(osp.join(output_dir, f'chr_{chrom}.hyp'))

        # Write the validation results:
        if args.fitting_strategy in ('GS', 'BO'):
            if args.genomewide:
                hs_m.write_validation_result(osp.join(output_dir, 'combined.validation'))
            else:
                hs_m.write_validation_result(osp.join(output_dir, f'chr_{chrom}.validation'))

        # Cleanup:
        gdl.cleanup()
        if validation_gdl is not None:
            validation_gdl.cleanup()

        if args.fitting_strategy != 'BMA':
            h2g.append(m_h2g)
            prop_causal.append(m_p)

    if args.fitting_strategy != 'BMA' and args.chrom is None:
        print(">>> Total heritability for the trait:", np.sum(h2g))

        if np.sum(h2g) > 1.:
            print("Warning: The estimated heritability has a value greater than 1. "
                  "This is indicative of poor model fit or the algorithm diverging. "
                  "You may need to re-run this model with a different LD panel.")

        hyp_df = pd.DataFrame.from_dict({
            'Heritability': np.sum(h2g),
            'Prop. Causal': np.mean(prop_causal)
        }, orient='index')

        hyp_df.to_csv(osp.join(output_dir, 'combined.hyp'))


if __name__ == '__main__':
    main()

