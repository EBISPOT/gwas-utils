#!/bin/bash

logs="/hps/nobackup/parkinso/spot/gwas/data/sumstats/harmonisation/logs/"

sbatch --output="${logs}/refresh.out" --error="${logs}/refresh.err" --partition=datamover --mem=4000 --wrap="cd /hps/software/users/parkinso/spot/gwas/prod/sw/harmonisation; cp hq.db hq.db.bak; source /hps/software/users/parkinso/spot/gwas/anaconda3/bin/activate; conda activate gwas-utils; queue-harmonisation --action refresh --source_dir /nfs/production/parkinso/spot/gwas/prod/data/summary_statistics --ftp_dir /nfs/ftp/public/databases/gwas/summary_statistics --harmonisation_dir /hps/nobackup/parkinso/spot/gwas/data/sumstats/harmonisation/toharm"