import pandas as pd
import glob
import os.path as osp

results = []

for phe_f in glob.glob("data/phenotypes/*/*/*.txt"):

    trait_type, config, trait = phe_f.split("/")[2:]
    trait = trait.replace(".txt", "")

    trait_df = pd.read_csv(phe_f, names=['FID', 'IID', 'phenotype'], sep="\t")

    if config == 'real':
        train_files = glob.glob(f"data/keep_files/ukbb_cv/{trait_type}/{trait}/*/train.keep")
    else:
        train_files = ["data/keep_files/ukbb_train_subset.keep"]

    for train_f in train_files:
        train_df = pd.read_csv(train_f, sep="\t", names=['FID', 'IID'])
        merged_df = train_df.merge(trait_df)

        if config == 'real':
            gwas_config = 'real_' + osp.basename(osp.dirname(train_f))
        else:
            gwas_config = config

        result = {
            'Trait': trait,
            'Configuration': gwas_config,
            'Class': trait_type,
            'N': len(merged_df)
        }

        if trait_type == 'binary':
            n_cases = merged_df['phenotype'].sum()
            n_controls = len(merged_df) - n_cases
            result['N_eff'] = 4./(1./n_cases + 1./n_controls)
        else:
            result['N_eff'] = result['N']

        results.append(result)


final_df = pd.DataFrame(results)
final_df.to_csv("metadata/n_eff_table.txt", sep="\t", index=False)
