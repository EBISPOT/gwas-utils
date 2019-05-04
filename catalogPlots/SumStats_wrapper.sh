#!/usr/bin/env bash

# path to script:
base=${0%/*}/;

# Get date:
today=$(date "+%Y-%m-%d")

# This function provides help on the usage of the script:
function display_help {
    message=${1};
    echo -e "\n$message";

    echo ""
    echo "Fetches yearly counts for studies and publications"
    echo "with and without summary statistics."
    echo "Then creates nice barplots"
    echo "(For more information: dsuveges@ebi.ac.uk)"

    echo ""
    echo "Usage: $0 -y <startYear> -h"
    echo ""
    echo "  -y first year to consider (>2010), default: 2015"
    echo "  -h print out this help message and exit"
    echo ""
    echo ""

    exit 1;
}

# To enable shared utils eg. database connection add this to python path:
export PYTHONPATH=/nfs/spot/sw/prod/gwas/scripts/shared_utils:${PYTHONPATH}

# To enable database connection for any user add (spotbot knows about these):
export LD_LIBRARY_PATH=/nfs/spot/tools/oracle/instantclient_12_2:${LD_LIBRARY_PATH}

# testing command line arguments:
OPTIND=1
while getopts "hy:" opt; do
    case "$opt" in
        'y' ) startYear=${OPTARG} ;;
        'h' | * ) display_help ;;
    esac
done

# Testing if start year is specified:
if [[ -z ${startYear} ]]; then
    startYear=2015
elif [[ $(echo $startYear | perl -lane '$_ =~ /(^20\d{2}$)/; $_ eq $1 ? print 0 : print 1;') == 1 ]]; then
    echo "[Error] Provided year value ($startYear) is not valid. Exiting."; exit 1
fi

dataTable="SummaryStats_table.${today}.csv"

## Calling Python script to fetch data from database:
echo "[Info] Fetching data from database..."

# Activating virtual environment:
source /nfs/spot/tools/anaconda3/bin/activate
conda activate gwas-utils

# Calling any python script:
python ${base}/SumStats_fetch_table.py --filename  ${dataTable}

exitCode=$?

# De-activate environment
conda deactivate

# Testing if the file exists:
if [[ ! -f "${dataTable}" ]];then
    echo "[Error] Data file (${dataTable}) was not generated. Exiting."; exit 1;
else
    echo "[Info] Data file (${dataTable}) is saved."
fi

# Calling the R script:
echo "[Info] Plotting... "
Rscript --vanilla ${base}/SumStats_plotter.R "${startYear}" "${dataTable}"


