#!/bin/bash

ref=$1
all_harm_folder=$2
ftp=$3
failed=$4
version=$5
wd=$6

# ENV VARS

export NXF_SINGULARITY_CACHEDIR=$SINGULARITY_CACHEDIR

# Load modules

module load openjdk-16.0.2-gcc-9.3.0-xyn6nf5
module load nextflow-21.10.6-gcc-9.3.0-tkuemwd
module load singularity-3.7.0-gcc-9.3.0-dp5ffrp


# Nextflow command

cd $wd

NXF_VER=22.05.0-edge nextflow run EBISPOT/gwas-sumstats-harmoniser\
 -r $version\
 --ref $ref\
 --all_harm_folder $all_harm_folder\
 --ftp $ftp\
 --failed $failed\
 --gwascatalog\
 -profile cluster,singularity
