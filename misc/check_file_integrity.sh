#!/bin/bash
#SBATCH --job-name=check_file_integrity
#SBATCH --time=3-00:00:00
#SBATCH --mem=64G
#SBATCH --cpus-per-task=1
#SBATCH --partition=datamover
#SBATCH --mail-type=ALL
#SBATCH --mail-user=<your email address>

# Dir for .gz files
DIR="/hps/nobackup/parkinso/spot/gwas/scratch/goci-1267/aws/formatted_long/gwas_summary_stats/"

LOGFILE="/hps/nobackup/parkinso/spot/gwas/scratch/goci-1267/scripts/corrupt_files.log"
> $LOGFILE

check_file() {
    local file=$1
    if ! gunzip -t "$file" 2>>$LOGFILE; then
        echo "$file is corrupt" >> $LOGFILE
    else
        echo "$file is OK"
    fi
}

export -f check_file
export LOGFILE

find "$DIR" -name "*.gz" -exec bash -c 'check_file "$0"' {} \;

if [ -s $LOGFILE ]; then
    echo "Some files are corrupt. See $LOGFILE for details."
else
    echo "All files are OK."
fi
