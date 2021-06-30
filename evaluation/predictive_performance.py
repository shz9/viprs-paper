import pandas as pd
from scipy import stats
import glob
import os.path as osp
import sys
sys.path.append(osp.dirname(osp.dirname(__file__)))
from utils import makedir
import functools
print = functools.partial(print, flush=True)


def evaluate_predictive_performance(true_phenotype, pred_phenotype):

    _, _, r_val, _, _ = stats.linregress(pred_phenotype, true_phenotype)

    return {
        'R2': r_val**2
    }


print("> Evaluating predictive performance of PRS methods...")

for trait_f in glob.glob("data/phenotypes/*/*.txt"):

    pheno_df = pd.read_csv(trait_f, names=['FID', 'IID', 'phenotype'], sep="\s+")
    config, trait = trait_f.split("/")[2:]
    print("> Configuration:", config, " | Trait:", trait)
    trait = trait.replace(".txt", "")

    pheno_res = []

    for prs_m_dir in glob.glob(f"data/test_scores/*/*/{config}/{trait}"):

        ld_panel, model = prs_m_dir.split("/")[2:4]
        print(f"> Evaluating {model} ({ld_panel})")
        prs_files = glob.glob(osp.join(prs_m_dir, "*.pprs"))

        if (config == 'real' and len(prs_files) != 22) or len(prs_files) < 1:
            print(f"> Some scoring files are missing for {ld_panel}/{model}. Skipping evaluation...")
            continue

        prs_df = None

        for prs_file in prs_files:
            df = pd.read_csv(prs_file, sep="\s+").set_index(['FID', 'IID'])

            if prs_df is None:
                prs_df = df
            else:
                prs_df = prs_df.add(df)

        prs_df = prs_df.reset_index()

        merged_df = pheno_df.merge(prs_df).dropna()
        res = evaluate_predictive_performance(merged_df['phenotype'], merged_df['PRS'])
        res.update({
            'Trait': trait,
            'LD Panel': ld_panel,
            'Model': model,
        })

        pheno_res.append(res)

    eval_pheno_df = pd.DataFrame(pheno_res)

    if config != 'real':
        _, h2, _, p = config.split("_")
        eval_pheno_df['Heritability'] = float(h2)
        eval_pheno_df['Prop. Causal'] = float(p)

    makedir(f"data/evaluation/{config}/")
    eval_pheno_df.to_csv(f"data/evaluation/{config}/{trait}.csv", index=False)

