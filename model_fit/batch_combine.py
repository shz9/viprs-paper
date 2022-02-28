import argparse
from combine_fit_files import combine_fit_files, combine_hyp_files, combine_validation_files
from multiprocessing import Pool
import glob


def combine(d):
    print(d)
    try:
        combine_fit_files(d)
    except Exception as e:
        print(e)

    try:
        combine_hyp_files(d)
    except Exception as e:
        print(e)

    try:
        combine_validation_files(d)
    except Exception as e:
        print(e)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Combine model fit results into a single file.')
    parser.add_argument('-d', dest='directory', type=str, required=True,
                        help='The pattern of directories to search under')
    args = parser.parse_args()

    pool = Pool(10)
    pool.map(combine, glob.glob(args.directory))
    pool.close()
    pool.join()
