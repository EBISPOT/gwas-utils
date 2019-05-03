#!/usr/bin/env bash


##
## Wrapper script to execute quality control as part of the GWAS Catalog data release.
##

# To enable shared utils eg. database connection add this to python path:
export PYTHONPATH=/nfs/spot/sw/prod/gwas/scripts/shared_utils:${PYTHONPATH}

# To enable database connection for any user add (spotbot knows about these):
export LD_LIBRARY_PATH=/nfs/spot/tools/oracle/instantclient_12_2:${LD_LIBRARY_PATH}

# If parameters are expected to be passed downwards:
OPTIND=1
while getopts "e:r:p:s:f:" opt; do
    case "$opt" in
        'e' ) email="${OPTARG}" ;;
        'r' ) relDB="${OPTARG}" ;;
        'p' ) prodDB="${OPTARG}" ;;
        's' ) newSolr="${OPTARG}" ;;
        'f' ) oldSolr="${OPTARG}" ;;
    esac
done

# Activating virtual environment:
source /nfs/spot/tools/anaconda3/bin/activate
# conda activate gwas-utils

# If the script directory is used down the line:
scriptDir=${0%/*}/;

# Calling QC script:
python studyQC.py --oldSolrAddress ${oldSolr} \
                  --newSolrAddress ${newSolr} \
                  --fatSolrCore gwas \
                  --document study \
                  --productionDB ${prodDB} \
                  --releaseDB ${relDB} \
                  --emailAddress ${email}

# Save exitcode:
exitCode=$?

# De-activate environment
conda deactivate

# Exit with the exit code of the python script:
exit ${exitCode}


