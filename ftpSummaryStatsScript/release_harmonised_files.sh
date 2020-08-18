#!/bin/bash

harmonise_dir=$1
release_dir=$2
ftp_dir=$3
reports=$4

if [ $ftp_dir ]; then
    :
else
    echo "provide an FTP dir"
    exit 0
fi


for f in $harmonise_dir/*; do

    # identify harmonied files that need releasing
    if [ $(find $f -maxdepth 1 -mmin +30 -type f -name harmonised.qc.tsv) ] ; then

        echo $f

        # set vars
        file_id=$(basename $f)
        file_id_no_build=$(echo $file_id | sed 's/-[bB]uild.*//g' )
        gcst=$(echo $file_id | cut -f2 -d '-' )

        # prep dirs
        mkdir -p $release_dir/$gcst
        mkdir -p $release_dir/$gcst/harmonised

        # compress harmonised file
        gzip -c  $f/harmonised.qc.tsv > $release_dir/$gcst/harmonised/$file_id_no_build.h.tsv.gz
        # compress associated formatted file
        gzip -c $f.tsv > $release_dir/$gcst/harmonised/$file_id.f.tsv.gz

        # generate md5sums for these files
        md5sum $release_dir/$gcst/harmonised/$file_id_no_build* > $release_dir/$gcst/harmonised/md5sum.txt

        # release to FTP
        # identify the remote directory - this find matches the GCST for the end of the dirname
        remote=$(find $ftp_dir -maxdepth 1 -type d -name "*_$gcst")
        if [[ $remote ]]; then
            echo $remote
            rsync -rv $release_dir/$gcst/harmonised $remote/

            # clean up harmonised, formatted and raw files
            rm $f.tsv
            mv $f/report.txt $reports/${gcst}_report.txt
            rm -r $f
        fi
    fi
don
