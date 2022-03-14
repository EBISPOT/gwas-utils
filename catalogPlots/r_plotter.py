import subprocess
import argparse
import sys
from os import path

r_script_names = {
                  "sumstats": "SumStats_plotter.R",
                  "ta_vs_gwas": "TA_vs_GWAS_publication.R"
                  }


def execute_r_script(plotter, other_args):
    r_script_path = path.join(sys.prefix, "r_scripts", r_script_names[plotter])
    cmd = ["Rscript", "--vanilla", r_script_path]
    cmd.extend(other_args)
    print(' '.join(cmd))
    return subprocess.run(cmd)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--plotter',
                        type=str,
                        help='Plotter to use. Choose `sumstats` for SumStats_plotter.Rl; \
                        choose `ta_vs_gwas` for TA_vs_GWAS_publication.R',
                        choices=[k for k in r_script_names],
                        required=True)
    parser.add_argument('other_args', nargs='*')
    args = parser.parse_args()
    plotter = args.plotter
    other_args = args.other_args
    execute_r_script(plotter, other_args)


if __name__ == '__main__':
    main()
