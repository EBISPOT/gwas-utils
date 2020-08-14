#!/bin/bash

# This checks the gwas_cat private ftp for files that were submitted and need publishing.
# The files have gone through the depo app and have undergone:
#     1) successful depo app validation
#
# These files simply need to be moved from the 'deposition app private FTP validation successful' dir
# to our staging area.
# Then move the file out of the depo app staging and into ready to harmoise dir (harmonise_dir)

source_dir=$1
staging_dir=$2
harmonise_dir=$3

# need to chmod so everyone can read
for f in $source_dir/*; do
        if [ -e "$f" ]; then
                rsync -rv --chmod=Du=rwx,Dg=rx,Do=rx,Fu=rw,Fg=r,Fo=r $f $staging_dir/
                mv -v $f $harmonise_dir/
        fi
done
