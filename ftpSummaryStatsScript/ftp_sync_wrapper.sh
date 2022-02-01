set -e

stagingDir=$1
ftpDir=$2
queue=$3
logDir=$4
condaPath=$5
condaEnv=$6
emailFrom=$7
emailRecipient=$8 # can provide a comma separated list

# call python script to sync sumstats

echo "Performing sync..."
cd $logDir
mkdir -p $logDir/ftp_sync
echo "LSF logs: ${logDir}/ftp_sync"

source $condaPath
conda activate $condaEnv

bsub -oo $logDir/ftp_sync/ftp_sync.o -eo $logDir/ftp_sync/ftp_sync.e -K -q $queue -g "/gwas_ftp_sync" "ftp_sync \
	--stagingDir $stagingDir \
	--ftpDir $ftpDir \
	--apiURL 'https://www.ebi.ac.uk/gwas/curation/api/v1/public/' \
	--emailFrom $emailFrom \
	--emailRecipient $emailRecipient"

echo "Regenerating harmonised list..."
echo "LSF logs: ${logDir}/ftp_sync/harm_list"
bsub -oo $logDir/ftp_sync/harm_list.o -eo $logDir/ftp_sync/harm_list.e -q $queue -g "/gwas_ftp_sync" "cd $ftpDir && find . -name "*.h.tsv.gz" > harmonised_list.txt"
