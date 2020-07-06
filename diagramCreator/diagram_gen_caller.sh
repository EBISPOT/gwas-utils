#!/usr/bin/env bash

# Capture absolute path for the script:
scriptDir=${0%/*}/;

# Links to files: Needs to be updated for all the environments:
jarLocation=/nfs/spot/sw/prod/gwas/applications/diagram-generator
propLocation=/nfs/spot/sw/prod/gwas/config

today=$( date '+%Y-%m-%d')

# Data folder:
dataFolder=${1} # Path where the diagram svg is saved.

# The file name is built in:
fileName=4FF04FDA193DF9FBCB6333FD8AEC0BD6F29EA0D4.svg
pvaluemax=5e-8
#datemax=2012-01-01

# Smaller diagram for testing purposes:
# fileName=A7A915BBF3302F0673B0FE592668F480CC84CCE5.svg
# query="pvaluemax=5e-8&datemax=2012-01-01"

# Report input options:
echo "[Info] Calling goci-diagram-gen.jar."
echo "[Info] Output folder: ${dataFolder}"
echo "[Info] Expected file name: ${fileName}"
echo ""

# Handling existing file:
if [[ -f ${dataFolder}/${fileName} ]]; then
    # 1. calculate md5 sum:
    oldMd5=$(md5sum ${dataFolder}/${fileName} | cut -f1 -d" ")

    # 2. Backing up file:
    echo "[Info] Backing up old file: ${dataFolder}/${fileName} -> ${fileName/svg/${today}.svg}"
    mv  ${dataFolder}/${fileName}  ${dataFolder}/${fileName/svg/${today}.svg}
else
    oldMd5=0
fi

# 3. Calling generator:
 java -Dcatalina.base=. -Xmx4g -DentityExpansionLimit=10000 \
 -Djavax.servlet.request.encoding=UTF-8 -Dfile.encoding=UTF-8 \
 -Dspring.config.location=${propLocation}/application.properties -Xmx4G \
 -jar /nfs/spot/sw/prod/gwas/applications/diagram-generator/goci-diagram-gen.jar \
 --pvaluemax ${pvaluemax}  --output ${dataFolder}/${fileName}


# 7. Check if the file is actually an svg:
if [[ ! -f ${dataFolder}/${fileName} ]]; then
    echo "${dataFolder}/${fileName}"
    echo "[Error] The expected output does not exist. Exiting."
    exit 1;
fi

# 5. Check if the output is an svg or what:
read chromosomeCnt assocCnt <<<$(cat ${dataFolder}/${fileName} | perl -lane '@a = $_ =~ /"(Chromosome.+?)"/g; @b = $_ =~ /(circle)/g; $chrom += scalar @a; $assoc += scalar @b; END{print "$chrom $assoc"}')
echo "[Info] in the svg file there are ${chromosomeCnt} chromosomes and ${assocCnt} associations."

if [[ -z $chromosomeCnt || -z $assocCnt ]]; then
    echo "[Error] The output file is empty or not an svg. Script failed. Exiting"
    exit 1;
fi

# 6. Compare md5sums:
newMd5=$(md5sum ${dataFolder}/${fileName} | cut -f1 -d" ")
if [[ $oldMd5 == $newMd5 ]]; then
    echo "[Warning] The md5 sum of the newly generated svg file is the same as the old one..."
else
    echo "[Info] The md5 sum of the newly generated file is different from the old one."
fi

