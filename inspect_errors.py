import argparse
import subprocess


def inspect_log_files(path, error_terms=('error', 'OptimizationDivergence', 'Exception')):

    for err in error_terms:
        try:
            output = subprocess.check_output(f"grep -i '{err}' {path}",
                                             shell=True, stderr=subprocess.STDOUT).decode()
        except subprocess.CalledProcessError as e:
            output = e.output.decode()

        if len(output) > 0:
            print("------------------------------------------------------------------------")
            print(f"The log files at {path} contain one or more error terms.\nSearch term: {err}")
            print("&& && && && && && && && && && && && && && && && && && && && && && && && ")
            print(output)
            return False

    return True


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Search for errors or exceptions in the log files.')
    parser.add_argument('-d', '--log-dir', dest='log_dir', type=str, required=True,
                        help='The log dir to search for errors in (may contain wildcards)')
    args = parser.parse_args()

    print("Error free:", inspect_log_files(args.log_dir))
