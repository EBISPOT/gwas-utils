#!/bin/bash

#  1. Runs harmonisation pipeline on all tsv files in $toharmonise
#  2. If/when successful, those harmonised files are released to the $ftp_dir and the $api_load

toharmonise=$1 # dir where tsv files are ready to be harmonised
snakemake_dir=$2 # dir where https://github.com/EBISPOT/gwas-sumstats-harmoniser/blob/master/Snakefile is
release_dir=$3 # dir for staging completed files for release
ftp_dir=$4 # ftp parent dir
reports=$5 # reports dir
api_load=$6 # loading dir for the SumStats HDF5 API loader
venv=$7 #.env/bin/activate

source $venv
cd $snakemake_dir

for f in $toharmonise/*.tsv; do
    if [ -e $f ]; then
        n=$(echo $f | sed "s/.tsv//g")
        h=$n/harmonised.qc.tsv
        # if job already running or snakemake target already exists.
        if bjobs -w | grep -q $n || [ $(find $n -maxdepth 1 -mmin +30 -type f -name harmonised.qc.tsv) ] ; then
            if snakemake  -n -d $n --configfile $snakemake_dir/config.yaml --profile lsf $h  | tail -n1 | grep "Nothing to be done."; then
                echo "$h --> Ready to release"

                # set vars
                file_id=$(basename $n)
                file_id_no_build=$(echo $file_id | sed 's/-[bB]uild.*//g' )
                gcst=$(echo $file_id | cut -f2 -d '-' )

                # prep dirs
                mkdir -p $release_dir/$gcst
                mkdir -p $release_dir/$gcst/harmonised

                # compress harmonised file
                echo "compressing files"
                gzip -v -c  $n/harmonised.qc.tsv > $release_dir/$gcst/harmonised/$file_id_no_build.h.tsv.gz
                rsync -pv --chmod=Du=rwx,Dg=rwx,Do=rx,Fu=rw,Fg=rw,Fo=r $n/harmonised.qc.tsv $api_load/$file_id_no_build.tsv
                # compress associated formatted file
                gzip -v -c $f > $release_dir/$gcst/harmonised/$file_id.f.tsv.gz

                # generate md5sums for these files
                md5sum $release_dir/$gcst/harmonised/$file_id_no_build* > $release_dir/$gcst/harmonised/md5sum.txt

                # release to FTP
                # identify the remote directory - this find matches the GCST for the end of the dirname
                remote=$(find $ftp_dir -maxdepth 1 -type d -name "*_$gcst")
                if [[ $remote ]]; then
                    echo $remote
                    rsync -prv --chmod=Du=rwx,Dg=rwx,Do=rx,Fu=rw,Fg=rw,Fo=r $release_dir/$gcst/harmonised $remote/

                    # clean up harmonised, formatted and raw files
                    rm -v $f
                    mv -v  $n/report.txt $reports/${gcst}_report.txt
                    rm -r $n
                fi
            else
                echo "$h --> Still working on it"
            fi
        else
            echo "Submitting $n for harmonisation"
            mkdir -p $n
            bsub "snakemake --rerun-incomplete -d $n --configfile $snakemake_dir/config.yaml --profile lsf $h"
        fi
    else
        echo "$f doesn't exist, there's nothing to do."
    fi
done
