#!/bin/bash

logs="/hps/nobackup/parkinso/spot/gwas/data/sumstats/harmonisation/logs/"
day=$(date "+%Y%m%d")

bsub -q datamover -oo "${logs}/pre-gwas-ssf.out" -eo "${logs}/pre-gwas-ssf.err" -M4000 -R "rusage[mem=4000]" "cd /hps/software/users/parkinso/spot/gwas/prod/sw/harmonisation; source /hps/software/users/parkinso/spot/gwas/anaconda3/bin/activate; conda activate gwas-utils; mkdir /hps/nobackup/parkinso/spot/gwas/data/sumstats/harmonisation/pre_gwas_ssf/toharm/${day}; queue-harmonisation --action release --source_dir /nfs/production/parkinso/spot/gwas/prod/data/summary_statistics --ftp_dir /nfs/ftp/public/databases/gwas/summary_statistics --harmonisation_dir /hps/nobackup/parkinso/spot/gwas/data/sumstats/harmonisation/pre_gwas_ssf/toharm/${day} --number 20 --harmonisation_type v0"