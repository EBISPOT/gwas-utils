#!/bin/bash

function get_jobid {
    output=$($*)
        echo $output | head -n1 | cut -d'<' -f2 | cut -d'>' -f1
    }

source activate sumstats
if snakemake ; then
  echo "rebuild snps"

  jobid=$(get_jobid bsub -M 56000 -R "rusage[mem=56000]" 'gwas-rebuild-snps')

  status=$(bjobs $jobid | tail -n1 | cut -f3 -d ' ')
  echo $jobid
  echo $status
  while [[ "$status" != "DONE" && "$status" != "EXIT" ]]; do
    echo $status
    status=$(bjobs $jobid | tail -n1 | cut -f3 -d ' ')
    sleep 60
  done
  echo "finished - ready to release"
fi
 
