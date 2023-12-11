#!/bin/bash

logs="/hps/nobackup/parkinso/spot/gwas/data/sumstats/harmonisation/logs/"

bsub -oo "${logs}/refresh.out" -eo "${logs}/refresh.err" -q datamover -M4000 -R "rusage[mem=4000]" "cd /hps/software/users/parkinso/spot/gwas/prod/sw/harmonisation; cp hq.db hq.db.bak; source /hps/software/users/parkinso/spot/gwas/anaconda3/bin/activate; conda activate gwas-utils; queue-harmonisation --action refresh --source_dir /nfs/production/parkinso/spot/gwas/prod/data/summary_statistics --ftp_dir /nfs/ftp/public/databases/gwas/summary_statistics --harmonisation_dir /hps/nobackup/parkinso/spot/gwas/data/sumstats/harmonisation/toharm"