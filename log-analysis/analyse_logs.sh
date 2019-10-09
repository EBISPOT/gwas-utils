#!/usr/bin/env bash

# This script was written to parse log files. It can handle different types as well: REST, search, download.
# To find out which is going to analysed, parse from command line argument:

function checkDate (){
    if [[ -z $( echo $1 | perl -lane 'print "OK" if $_ =~ /\d{4}-\d{2}-\d{2}/' ) ]]; then echo "[Error] Date ($1) is not suitable. Expected format: YYYY-MM-DD. Exiting."; exit 2; fi
}

declare -A docTypes=(
    [REST]="rest/api"
    [search]="/gwas/search.query="
    [download]="/gwas/api/search/downloads"
    [dedicatedPages]="/gwas/"
)


# Get script directory:
export scriptDir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# is the document type specified? If not exit.
if [[ -z $1 ]]; then
    echo "[Error] Document type needs to be specified! (REST, search or download). Exiting."
    exit 1;
elif [[ -z ${docTypes[$1]} ]]; then
    echo "[Error] Document type ($1) is not supported! Choose from: REST, search or download. Exiting."
    exit 1;
else
    source=$1
fi

# Check if we need to use the default values or not:
if [[ -z $2 ]]; then
    echo "[Warning] No start date is submitted. ${date1} will be used." >&2
else
    checkDate $2
    fromDate=$2
fi 

if [[ -z $3 ]]; then
    echo "[Warning] No end date is submitted. Current date (${date2}) will be used." >&2
else
    checkDate $3
    toDate=$3
fi 


# Print out report:
echo "[Info] Selected document type: ${1}, regexp patten: ${docTypes[$source]}" >&2

export fromDate
export toDate
export pattern=${docTypes[$source]}
export source

if [[ $source == 'dedicatedPages' ]]; then
    cat /dev/stdin | "${scriptDir}"/date_filter.sh ${fromDate} ${toDate} | xargs cat | perl -MData::Dumper -lane 'BEGIN{
        sub get_top_15 {
            %h = ();
            foreach $x (@{$_[0]}){ $h{$x}++ };
            my $topTerms = {};
            foreach $x (sort { $h{$b} <=> $h{$a} } keys %h){
                $topTerms->{$x} = $h{$x};
                last if scalar keys %{$topTerms} == 15
            }
            return $topTerms
        };
        %endpoints = (
            genes => [], 
            publications => [],
            variants => [],
            regions => [],
            studies => [],
            efotraits => []
        );
    }{
        ($endpoint, $entity) = $_ =~ /GET \/gwas\/(.+?)\/(.+?) HTTP/; 
        push @{$endpoints{$endpoint}}, $entity if exists $endpoints{$endpoint};
    } END {
        # Saving basic stats:
        $statFile=sprintf("%s_%s-%s_stats.tsv", $ENV{"source"}, $ENV{"fromDate"}, $ENV{"toDate"});
        open($STATS, ">", $statFile);
        foreach $ep (keys %endpoints){
            printf $STATS "%s\t%s\n", $ep, scalar(@{$endpoints{$ep}})
        }

        # Saving top 10 viewed pages:
        $topFile=sprintf("%s_%s-%s_topPages.tsv", $ENV{"source"}, $ENV{"fromDate"}, $ENV{"toDate"});
        open($topFile, ">", $topFile);
        foreach $ep (keys %endpoints){
            print $topFile "$ep";
            $topHash = get_top_15($endpoints{$ep});
            foreach $x (sort { $topHash->{$b} <=> $topHash->{$a} } keys %{$topHash}){
                printf $topFile "%s\t%s\n", $x, $topHash->{$x}
            }
        }
    }'

else

    cat /dev/stdin | "${scriptDir}"/date_filter.sh ${fromDate} ${toDate}  | xargs cat | perl -lane 'BEGIN{ 
                %searchTerms = (); 
                $fullData = 0; 
                $searchCnt = 0; 
                $failed = 0;
            }
            {
                ($searchTerm, $exitCode, $data) = $_ =~ /$ENV{"pattern"}(\S+)\s+\S+\s+(\d+)\s+(\d+)/; 
                next unless $searchTerm;
                $searchCnt ++;
                $failed ++ if $exitCode != 200;
                $fullData += $data;
                $searchTerms{$searchTerm} ++;
            } END {
                # Saving stats:
                $statFile=sprintf("%s_%s-%s_stats.tsv", $ENV{"source"}, $ENV{"fromDate"}, $ENV{"toDate"});
                open($STATS, ">", $statFile);

                # Printing header:
                print $STATS "Period\tType\tQueriesCnt\tFailedCnt\tData";
                print $STATS join "\t", ($ENV{"fromDate"}."-".$ENV{"toDate"}, $ENV{"source"}, $searchCnt,  $failed, $fullData);

                # Saving query data:
                $queryFile=sprintf("%s_%s-%s_queries.tsv", $ENV{"source"}, $ENV{"fromDate"}, $ENV{"toDate"});
                open($QUERY, ">", $queryFile);

                foreach $term  (sort {$searchTerms{$b} <=> $searchTerms{$a}} keys %searchTerms ){
                    printf $QUERY "%s\t%s\n", $searchTerms{$term}, $term
                }
                
            }'
fi

exit 0