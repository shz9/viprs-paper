import argparse
import pandas as pd
import os
import os.path as osp
import glob


def combine_fit_files(fit_dir, delete_original=True):

    fit_files = list(glob.glob(osp.join(fit_dir, "chr_*.fit")))

    if len(fit_files) == 22:

        dfs = []
        for f in fit_files:
            dfs.append(pd.read_csv(f, sep="\t"))

        # Concatenate the tables:
        dfs = pd.concat(dfs)
        # Output a single, compressed table:
        dfs.to_csv(osp.join(fit_dir, "combined.fit.gz"), sep="\t", index=False)

        if delete_original:
            for f in fit_files:
                try:
                    os.remove(f)
                except OSError as e:
                    raise e
    elif osp.isfile(osp.join(fit_dir, "combined.fit.gz")):
        return
    elif len(fit_files) == 0:
        print("Error: There are no fit files in this directory!")
    else:
        print(f"Error: Directory {fit_dir} is incomplete!")


def combine_hyp_files(fit_dir, delete_original=True):

    hyp_files = list(glob.glob(osp.join(fit_dir, "chr_*.hyp")))
    fit_files = list(glob.glob(osp.join(fit_dir, "chr_*.fit")))

    if len(hyp_files) == 22:

        dfs = []
        for f in hyp_files:
            dfs.append(pd.read_csv(f, sep="\t"))
            dfs[-1]['CHR'] = osp.basename(f).replace(".hyp", "")

        # Concatenate the tables:
        dfs = pd.concat(dfs)
        # Output a single, compressed table:
        dfs.to_csv(osp.join(fit_dir, "combined.hyp.gz"), sep="\t", index=False)

        if delete_original:
            for f in hyp_files:
                try:
                    os.remove(f)
                except OSError as e:
                    raise e
    elif osp.isfile(osp.join(fit_dir, "combined.hyp.gz")):
        return
    elif len(hyp_files) == 0 and ((len(fit_files) == 22) or osp.isfile(osp.join(fit_dir, "combined.fit.gz"))):
        print("Warning: This model does not output hyperparameter files!")
    elif len(hyp_files) == 0:
        print("Error: There are no hyperparameter files in this directory!")
    else:
        print(f"Error: Directory {fit_dir} is incomplete!")


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Combine model fit results into a single file.')
    parser.add_argument('-d', '--fit-dir', dest='fit_dir', type=str, required=True,
                        help='The directory to tidy and clean up')
    args = parser.parse_args()

    try:
        combine_fit_files(args.fit_dir)
    except Exception as e:
        print(e)

    try:
        combine_hyp_files(args.fit_dir)
    except Exception as e:
        print(e)
