#!/bin/bash

# ---------important-----------------
file_type="pre_gwas_ssf"
wrapper="/hps/software/users/parkinso/spot/gwas/prod/scripts/gwas-utils/harmonisationUtils/harmonisation_wrapper_slurm.sh"

# ----No change--------------------------
day=$(date -d "yesterday 13:00" "+%Y%m%d")
logs="/hps/nobackup/parkinso/spot/gwas/data/sumstats/harmonisation/pre_gwas_ssf/logs/${day}"
ref="/hps/nobackup/parkinso/spot/gwas/data/sumstats/harmonisation/resources"
to_harm="/hps/nobackup/parkinso/spot/gwas/data/sumstats/harmonisation/pre_gwas_ssf/toharm/${day}"
pub_ftp="/nfs/ftp/public/databases/gwas/summary_statistics"
failed="/hps/nobackup/parkinso/spot/gwas/data/sumstats/harmonisation/pre_gwas_ssf/failed/${day}"
mail_add="gwas-dev-logs@ebi.ac.uk"

# ----Changed part (include the content of the file)--------------------------
nf_conf="/hps/software/users/parkinso/spot/gwas/prod/scripts/cron/container_pre_ssf_slurm.config"
version="v1.0.8"
#-------------------------------------------------

cmd="${wrapper} ${ref} ${to_harm} ${pub_ftp} ${failed} ${version} ${logs} ${mail_add} ${file_type} ${nf_conf} ${day}"

if [[ -d "$to_harm"  ]]; then
        mkdir -p $logs
        sbatch --output="${logs}/nf.out" --error="${logs}/nf.err" --mem=8000 --time=50:00:00 --job-name=pre_gwas_ssf_harmo --wrap="${cmd}"
else
    	echo "Nothing to harmonise today"
fi