#!/usr/bin/env bash


function display_help (){

    echo "$1"
    echo "This script filters file names based on dates in the filenames. "
    echo ""
    echo "Usage:"
    echo -e "\tfind . -type f | $0 <from_date> <to_date> | xargs cat "
    echo ""
    echo "Where "
    echo -e "\tfrom_date : is the earlier date in YYYY-MM-DD format. Optional."
    echo -e "\to_date    : is the later date in YYYY-MM-DD format. Optional."
    echo ""
    echo "Format check for the date is performed."
    echo ""


    exit 1
}

function checkDate (){
    if [[ -z $( echo $1 | perl -lane 'print "OK" if $_ =~ /\d{4}-\d{2}-\d{2}/' ) ]]; then echo "[Error] Date ($1) is not suitable. Expected format: YYYY-MM-DD. Exiting."; exit 2; fi
}

# Accepting command line parameters:
OPTIND=1
while getopts "h" opt; do
    case "$opt" in
        "h" | *  ) display_help ;;
     esac
done

# Set default values for the dates:
export date1='1900-01-01'
export date2=$(date "+%Y-%m-%d")

# Check if we need to use the default values or not:
if [[ -z $1 ]]; then
    echo "[Warning] No start date is submitted. ${date1} will be used." >&2
else
    checkDate $1
    date1=$1
fi 

if [[ -z $2 ]]; then
    echo "[Warning] No end date is submitted. Current date (${date2}) will be used." >&2
else
    checkDate $2
    date2=$2
fi 

# Report parameters:
echo "[Info] Filtering logfiles between $date1 and $date2." >&2


cat /dev/stdin | perl -MTime::Piece -lane 'BEGIN{
            $atime = Time::Piece->strptime($ENV{"date1"}, "%Y-%m-%d");
            $btime = Time::Piece->strptime($ENV{"date2"}, "%Y-%m-%d");
            printf STDERR "[Info] Logfiles between %s and %s are selected only.\n" , $atime, $btime;
            $file_counter = 0;
        }{
            next unless $_ =~ /(\d{4}-\d{2}-\d{2})/; 
            $fdate = Time::Piece->strptime($1, "%Y-%m-%d"); 
            if( $fdate >= $atime && $fdate <= $btime){ print $_ ; $file_counter ++ }
        } END {print STDERR "[Info] Number of logfiles between the selected period: $file_counter."}'

