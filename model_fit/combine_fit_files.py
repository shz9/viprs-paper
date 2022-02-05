import argparse
import pandas as pd
import os
import os.path as osp
import glob


def combine_fit_files(fit_dir, delete_original=True):

    chr_files = list(glob.glob(osp.join(fit_dir, "chr_*.fit")))

    if len(chr_files) == 22:

        dfs = []
        for f in chr_files:
            dfs.append(pd.read_csv(f, sep="\t"))

        # Concatenate the tables:
        dfs = pd.concat(dfs)
        # Output a single, compressed table:
        dfs.to_csv(osp.join(fit_dir, "combined.fit.gz"), sep="\t", index=False)

        if delete_original:
            for f in chr_files:
                try:
                    os.remove(f)
                except OSError as e:
                    raise e
    else:
        print(f"Error: Directory {fit_dir} is incomplete!")


def combine_hyp_files(fit_dir, delete_original=True):

    chr_files = list(glob.glob(osp.join(fit_dir, "chr_*.hyp")))

    if len(chr_files) == 22:

        dfs = []
        for f in chr_files:
            dfs.append(pd.read_csv(f, sep="\t"))
            dfs[-1]['CHR'] = osp.basename(f).replace(".hyp", "")

        # Concatenate the tables:
        dfs = pd.concat(dfs)
        # Output a single, compressed table:
        dfs.to_csv(osp.join(fit_dir, "combined.hyp.gz"), sep="\t", index=False)

        if delete_original:
            for f in chr_files:
                try:
                    os.remove(f)
                except OSError as e:
                    raise e
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
