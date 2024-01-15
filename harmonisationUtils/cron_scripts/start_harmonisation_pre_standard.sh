#!/bin/bash

day=$(date -d "yesterday 13:00" "+%Y%m%d")

logs="/hps/nobackup/parkinso/spot/gwas/data/sumstats/harmonisation/pre_gwas_ssf/logs/${day}"

wrapper="/hps/software/users/parkinso/spot/gwas/prod/scripts/gwas-utils/harmonisationUtils/harmonisation_wrapper.sh"
ref="/hps/nobackup/parkinso/spot/gwas/data/sumstats/harmonisation/resources"
to_harm="/hps/nobackup/parkinso/spot/gwas/data/sumstats/harmonisation/pre_gwas_ssf/toharm/${day}"
pub_ftp="/nfs/ftp/public/databases/gwas/summary_statistics"
failed="/hps/nobackup/parkinso/spot/gwas/data/sumstats/harmonisation/pre_gwas_ssf/failed/${day}"
version="v1.0.4"
mail_add="gwas-dev-logs@ebi.ac.uk"
file_type="pre_gwas_ssf"
nf_conf="/hps/software/users/parkinso/spot/gwas/prod/scripts/cron/container_pre_ssf.config"

cmd="${wrapper} ${ref} ${to_harm} ${pub_ftp} ${failed} ${version} ${logs} ${mail_add} ${file_type} ${nf_conf}"

if [[ -d "$to_harm"  ]]; then
	mkdir -p $logs
	bsub -o "${logs}/nf.out" -e "${logs}/nf.err" -M8000 -R "rusage[mem=8000]" -g /pre_gwas_ssf_harmo "$cmd"
else
	echo "Nothing to harmonise today"
fi
