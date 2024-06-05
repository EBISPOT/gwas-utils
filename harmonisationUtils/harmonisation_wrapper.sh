#!/bin/bash

ref=$1
all_harm_folder=$2
ftp=$3
failed=$4
version=$5
wd=$6
mail_add=$7
file_type=$8
nf_conf=$9
day=${10}
run_day=$(date "+%Y%m%d-%H-%M")
run_id=$file_type"_"$day"_on_"$run_day
# ENV VARS

# ENV VARS

export NXF_SINGULARITY_CACHEDIR=$SINGULARITY_CACHEDIR

# nextflow tower setting
#export TOWER_ACCESS_TOKEN=nf_tower_tokens
#export TOWER_WORKSPACE_ID=workspaceid
# Load modules

module load openjdk-16.0.2-gcc-9.3.0-xyn6nf5
module load nextflow-21.10.6-gcc-9.3.0-tkuemwd
module load singularity-3.7.0-gcc-9.3.0-dp5ffrp

# Update local nf repo from public

NXF_VER=22.05.0-edge nextflow pull EBISPOT/gwas-sumstats-harmoniser

# Nextflow command

cd $wd

nextflow -c $nf_conf \
run EBISPOT/gwas-sumstats-harmoniser \
 -name $run_id \
 -r $version \
 -N $mail_add \
 --ref $ref \
 --all_harm_folder $all_harm_folder \
 --ftp $ftp \
 --failed $failed \
 --gwascatalog \
 -profile cluster,singularity \
 -with-tower

