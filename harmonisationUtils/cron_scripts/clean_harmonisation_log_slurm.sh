#!/bin/bash
#SBATCH -o %j.out
#SBATCH -e %j.err
#SBATCH --time=6-00:00:00
#SBATCH --mem=1G
#SBATCH -J clean_log
#SBATCH --partition=datamover

# 1. Generate error message log by -> .nextflow.log exit 1 -> workdir -> .command.err last 2 lines
# 2. Clean the logs folder and toharm folder
day=$(date -d "last month 13:00" "+%Y%m%d")

# For gwas-ssf
gwas_ssf_logs="/hps/nobackup/parkinso/spot/gwas/data/sumstats/harmonisation/logs/${day}"
gwas_ssf_to_harm="/hps/nobackup/parkinso/spot/gwas/data/sumstats/harmonisation/toharm/${day}"
gwas_ssf_nf_log=$gwas_ssf_logs/.nextflow.log

gwas_ssf_error_path=$gwas_ssf_logs/error_path
gwas_ssf_error_message=$gwas_ssf_logs/${day}_error_message.log
gwas_ssf_lts_path=/lts/production/parkinso/gwas/harmonisation/logs/gwas_ssf

less $gwas_ssf_nf_log| grep "Task monitor" | grep " DEBUG" | grep "exit: 1;" |grep -vE 'chrMT|chrX|chrY'| awk '{print "date_"'"$day"'";"$0}' | awk -F'[; ]' '{for(i=1; i<=NF; i++) {if($i ~ /date_/) {gsub(/[date_]/, "", $i); date=$i}; if($i ~ /GWASCATALOGHARM_GWASCAT/) {gsub(/[NFCORE_GWASCATALOGHARM:GWASCATALOGHARM_GWASCATALOG:]/, "", $i); process=$i}; if($i ~ /GCST/) {gsub(/[()]/, "", $i); gcst=$i}; if($i == "exit:") {code=$(i+1)}; if($i == "workDir:") {workdir=$(i+1)}};print date, process, code, gcst, workdir}' | awk '!seen[$4]++' > $gwas_ssf_error_path

if [[ ! -z $gwas_ssf_error_path ]]
then 
    echo -e $day"\tThere is no error message" > $gwas_ssf_error_message
else
    cat $gwas_ssf_error_path | while read gwas_line 
    do
       gwas_wkdir=$(echo $gwas_line | awk '{print $5}')
       gwas_error_msg=$(tail -n 2 $gwas_wkdir/.command.err | tr '\n' ';')
       echo -e "$gwas_line\t$gwas_error_msg" >> $gwas_ssf_error_message
    done
fi

# move the log file to the /lts/production/parkinso
cp $gwas_ssf_error_message $gwas_ssf_lts_path/${day}_gwas_ssf_error_message.log
rm -r $gwas_ssf_to_harm
rm -r $gwas_ssf_logs

#--------------------------------------------------------------------------------
# for Pre-gwas-ssf
pre_gwas_ssf_logs="/hps/nobackup/parkinso/spot/gwas/data/sumstats/harmonisation/pre_gwas_ssf/logs/${day}"
pre_gwas_ssf_to_harm="/hps/nobackup/parkinso/spot/gwas/data/sumstats/harmonisation/pre_gwas_ssf/toharm/${day}"
pre_gwas_ssf_nf_log=$pre_gwas_ssf_logs/.nextflow.log

pre_gwas_ssf_out_error_path=$pre_gwas_ssf_logs/error_path
pre_gwas_ssf_out_error_message=$pre_gwas_ssf_logs/${day}_error_message.log
pre_gwas_ssf_lts_path=/lts/production/parkinso/gwas/harmonisation/logs/pre_gwas_ssf

less $pre_gwas_ssf_nf_log| grep "Task monitor" | grep " DEBUG" | grep "exit: 1;" |grep -vE 'chrMT|chrX|chrY'| awk '{print "date_"'"$day"'";"$0}' | awk -F'[; ]' '{for(i=1; i<=NF; i++) {if($i ~ /date_/) {gsub(/[date_]/, "", $i); date=$i}; if($i ~ /GWASCATALOGHARM_GWASCAT/) {gsub(/[NFCORE_GWASCATALOGHARM:GWASCATALOGHARM_GWASCATALOG:]/, "", $i); process=$i}; if($i ~ /GCST/) {gsub(/[()]/, "", $i); gcst=$i}; if($i == "exit:") {code=$(i+1)}; if($i == "workDir:") {workdir=$(i+1)}};print date, process, code, gcst, workdir}' | awk '!seen[$4]++' > $pre_gwas_ssf_out_error_path

if [[ ! -s $pre_gwas_ssf_out_error_path ]]
then 
    echo -e $day"\tThere is no error message" > $pre_gwas_ssf_out_error_message
else
    cat $pre_gwas_ssf_out_error_path | while read pre_gwas_line 
    do
       pre_gwas_wkdir=$(echo $pre_gwas_line | awk '{print $5}')
       pre_gwas_error_msg=$(tail -n 2 $pre_gwas_wkdir/.command.err | tr '\n' ';')
       echo -e "$pre_gwas_line\t$pre_gwas_error_msg" >> $pre_gwas_ssf_out_error_message
    done
fi
# move the log file to the /lts/production/parkinso
cp $pre_gwas_ssf_out_error_message $pre_gwas_ssf_lts_path/${day}_pre_gwas_ssf_error_message.log
rm -r $pre_gwas_ssf_to_harm
rm -r $pre_gwas_ssf_logs