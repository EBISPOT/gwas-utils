# Log file analyis

This repository contains scripts to analyse site access logs based on the provided criteria in a defined period of time.

Scripts in this repository assume all the logfiles are already fetched and ready to be analyzed. For instruction on how to fetch these logs from the GWAS Catalog VMs, see [confluence page](https://www.ebi.ac.uk/seqdb/confluence/pages/viewpage.action?pageId=64720227 ).

Log files contain data of the usage of the **REST API**, **search queries** and all the **data downloads** initiated from the UI. We can extract the number of submitted and failed queries, the transferred data and the queries themselves. Since the release of the new user interface and the dedicated pages in October 2018, the access of these pages is also available.

The following query types are available, next to the regular expression pattern based on which the corresponding rows from the log files are selected:

* **REST**: `rest/api`
* **download**: `/gwas/api/search/downloads`
* **search**: `/gwas/search.query=`
* **dedicatePages**: `/gwas/genes`, `/gwas/variants` etc.

The analysis has two steps:
1. Filtering log files based on the creation date (the script expects the files follow this pattern: `access_2015-04-10.log` to determine date based on the file name)
2. The selected files are then parsed for certain type of access.

## Dependencies

The shell scripts contain embeded Perl code using the [Time::Piece](https://metacpan.org/pod/Time::Piece) package that might not be part of the standard Perl installation.

## Usage

Extracting statistics from the logfiles between a given date period by specifying the start and end date (all dates are expected to be provided in a `YYYY-MM-DD` format, no guessing here!):

```bash
queryType='search' # Accepted options: REST, download, search, dedicatedPages
startDate='2018-06-01'
endDate='2018-08-31'

find ${logDir} -type f | ${scriptDir}/analyse_logs.sh ${queryType} ${startDate} ${endDate}
```

The above example extarcts statistics on the search queries between the period 2018.06.01 and 2018.08.31. (Provided dates are handled inclusive: both the end and start date will be included.)

Two files will be generated in the working directory:

* **search_2018-06-01-2018-08-31_queries.tsv**: list of search terms and counts how many times a given term was queried.

| query count | query term |
|---|---|
| 89553 | rs7329174 |
| 2807 | breast%20cancer |
| 990 | *&filter=recent |
| 652 | obesity |
| 572 | schizophrenia |
| 450 | body%20mass%20index |
| 423 | 6:16000000-25000000 |
| 417 | multiple%20sclerosis |
| 394 | Alzheimers%20disease |
| 382 | diabetes |

* **search_2018-06-01-2018-08-31_stats.tsv**: summary of the stats

| Period | Type | QueriesCnt | FailedCnt | Data |
|--------|------|------------|-----------|------|
| 2018-06-01-2018-08-31 | search | 453811 | 43 | 16548217602|

### Generate monthly stats

Wrapper for generating monthly statistics between two distant dates.

```bash
queryType='search' # Accepted options: REST, download, search, dedicatedPages
startDate='2017-08-01'
endDate='2018-08-31'

# Montly stats are pooled in a separate folde:
mkdir -p ${logDir}/montly_stats && cd ${logDir}/montly_stats

${scriptDir}/monthly_logs_wrapper.sh  -l ${logDir} -t ${queryType} -s ${startDate} -e ${endDate}
```

As this command can take a long time, it make sense to submit to the farm:

```bash
# Creating folder for lsf log files:
mkdir -p ${logDir}/lsf_logs
lsf_logs=${logDir}/lsf_logs

for queryType in search download REST; do
    bsub -J "${queryType}" -M3000 -R"select[mem>3000] rusage[mem=3000]" -o ${lsf_logs}/${queryType}.o -e ${lsf_logs}/${queryType}.e \
        "${scriptDir}/monthly_logs_wrapper.sh -l ${logDir} -t ${queryType} -s ${startDate} -e ${endDate}"
done
```

The required 3GB memory is a little bit too much, bit is always better to be on the safe side than having jobs failing because of reaching memory limit. Once the jobs are done, the stats can be pooled together in to a single table that allows an easy downstream analysis.

```bash
cat <(find . -name "${queryType}_*stats.tsv" | head -n1 | xargs head -n1 ) \
    <(grep -h -v Period ${queryType}_*stats.tsv ) > ${queryType}_combined_stats.tsv
```

Which generates the following table:

```
Period                 Type      QueriesCnt  FailedCnt  Data
2017-08-01-2017-08-31  download  4299        159        33620640548
2017-09-01-2017-09-30  download  7026        169        38247888144
2017-10-01-2017-10-31  download  4993        100        41153455914
2017-11-01-2017-11-30  download  6634        52         46478033591
2017-12-01-2017-12-31  download  7865        52         42402656504
2018-01-01-2018-01-31  download  5340        82         71159347967
2018-02-01-2018-02-28  download  5738        145        78756372764
2018-03-01-2018-03-31  download  1233737     66         63542193387
2018-04-01-2018-04-30  download  5550        85         62268608785
```

A combined table is also possible to create if we are interested in the counts across REST, downoad and search:

```bash
type=download
type2=REST
type3=search

cat <(echo "Period ${type} ${type2} ${type3}") \
    <(join <(join <(grep -h -v Period ${type}_*stats.tsv  | cut -f1,3) \
        <(grep -h -v Period ${type2}_*stats.tsv | cut -f1,3)) \
        <(grep -h -v Period ${type3}_*stats.tsv | cut -f1,3) | sort -k1,1) \
    > Combined_query_counts.txt
```
Which gives the following table:

```
Period                 download  REST    search
2017-08-01-2017-08-31  4299      603     58171
2017-09-01-2017-09-30  7026      756     59173
2017-10-01-2017-10-31  4993      27411   67054
2017-11-01-2017-11-30  6634      332994  93555
2017-12-01-2017-12-31  7865      605106  119346
2018-01-01-2018-01-31  5340      60158   145420
2018-02-01-2018-02-28  5738      238896  115866
2018-03-01-2018-03-31  1233737   203854  123238
2018-04-01-2018-04-30  5550      1664    118845
2018-05-01-2018-05-31  6496      455321  150549
2018-06-01-2018-06-30  6318      337056  128593
2018-07-01-2018-07-31  7098      364450  152316
2018-08-01-2018-08-31  7623      604860  172902
```

## More information

On the [Confluence page](https://www.ebi.ac.uk/seqdb/confluence/pages/viewpage.action?pageId=64720227) of the catalog statistics there might be further information.

