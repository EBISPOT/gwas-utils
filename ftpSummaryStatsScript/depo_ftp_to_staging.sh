#!/bin/bash

# This checks the gwas_cat private ftp for files that were submitted and need publishing.
# The files have gone through the depo app and have undergone:
#     1) successful depo app validation
#
# These files simply need to be moved from the 'deposition app private FTP validation successful' dir
# to our staging area. It should be run as a cronjob on a noah-login node.

source_dir=<depo app staging>
staging_dir=<sumstats staging path>

# need to chmod so everyone can read
rsync -rv --chmod=Du=rwx,Dg=rx,Do=rx,Fu=rw,Fg=r,Fo=r $source_dir $staging_dir
