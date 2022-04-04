#!/usr/bin/env bash

##
## Generate monthly report between two defined dates.
##

function display_help(){
    echo "This is wrapper to extract monthly report from GWAS log files."
    echo ""
    echo "Usage: $0 -l <log_file_dir> -t <query type> -s <start date> -e <end date> -h "
    echo ""
    echo "Where:"
    echo "    log file dir: directory with the already downloaded log files."
    echo "    query types : type of the available query: REST, download or search"
    echo "    start date  : date from the analysis starts"
    echo "    end date    : date until the analysis goes"
    echo "    -h          : print out this message and exit."
    echo ""
    echo ""

    exit 0
}

# Accepting command line parameters:
OPTIND=1
while getopts "h?l:t:s:e:" opt; do
    case "$opt" in
        "l" ) logDir="${OPTARG}" ;; # Directory containing the log files
        "t" ) docType="${OPTARG}" ;; # Type of the access type
        "s" ) startDate="${OPTARG}" ;; # start day of the data extraction
        "e" ) endDate="${OPTARG}" ;; # last day of the data extraction
        "h" | *  ) display_help ;;
     esac
done

# Testing folder:
if [[ -z "${logDir}" ]]; then 
    echo "[Error] The folder name under which the log files are kept is not given. Exiting."
    exit 1;
elif [[ ! -d "${logDir}" ]]; then
    echo "[Error] The provided log file folder ($logDir) does not exit. Exiting."
    exit 1;
fi

# Testing docs:
availableTypes="search REST download"
if [[ -z $docType ]]; then
    echo "[Error] Query type is not specified. Exiting."
    exit 2;
elif [[ ! "${availableTypes}" =~ $docType ]]; then
    echo "[Error] $docType is not a accepted query type. Choose from ${availableTypes}. Exitig."
    exit 2;
fi

# provided date values are not checked only for existence:
if [[ -z $startDate ]]; then
    echo "[Error] Start date has to be specified. Exiting."
    exit 3;
elif [[ -z $(echo $startDate | perl -lane 'print "OK" if $_ =~ /\d{4}-\d{2}-\d{2}/' ) ]]; then
    echo "[Error] Start date ($startDate) does not follow the expected format: YYYY-MM-DD. Exiting."
    exit 3;
fi
if [[ -z $endDate ]]; then
    echo "[Error] End date has to be specified. Exiting."
    exit 3;
elif [[ -z $(echo $endDate | perl -lane 'print "OK" if $_ =~ /\d{4}-\d{2}-\d{2}/' ) ]]; then
    echo "[Error] End date ($endDate) does not follow the expected format: YYYY-MM-DD. Exiting."
    exit 3;
fi

export endDate
export startDate

# Script dir with all the script:
scriptDir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

perl -MTime::Piece -le '
    $timepoint = Time::Piece->strptime($ENV{"startDate"}, "%Y-%m-%d");
    $last_date = Time::Piece->strptime($ENV{"endDate"}, "%Y-%m-%d");

    while ( $timepoint <= $last_date){
        $first_day = $timepoint->strftime("%Y-%m-%d");
        $last = $timepoint->month_last_day;
        $last_day = $timepoint->strftime("%Y-%m-$last");
        $timepoint = $timepoint->add_months(1);
        print "$first_day $last_day"
    }
' | while read fistDay lastDay; do
        find ${logDir} -type f | ${scriptDir}/analyse_logs.sh ${docType} ${fistDay} ${lastDay}
done