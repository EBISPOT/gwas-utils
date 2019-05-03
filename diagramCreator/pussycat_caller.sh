#!/usr/bin/env bash

today=$( date '+%Y-%m-%d')

# Tomcat credentials:
tcUser=tomcat
tcPw=tomcat

# The following parameters will be submitted via command line parameters:
host=${1} # Fisrt command line option
port=${2} # Second command line option

# Data folder:
dataFolder=${3} # Third command line option

# The file name is built in:
# fileName=4FF04FDA193DF9FBCB6333FD8AEC0BD6F29EA0D4.svg
# query='pvaluemax=5e-8'

# Smaller diagram for testing purposes:
fileName=A7A915BBF3302F0673B0FE592668F480CC84CCE5.svg
query="pvaluemax=5e-8&datemax=2012-01-01"

# Report input options:
echo "[Info] Calling pussycat application."
echo "[Info] Query: ${query}"
echo "[Info] Pussycat host: ${host}:${port}"
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

# 3. Calling pussycat:
echo -n "[Info] Calling pussycat application..."
curl -s -f "http://${host}:${port}/gwas/pussycat/gwasdiagram/associations?${query}" > /dev/null &
sleep 30s

# 4. Keep checking if any session is running:
while true; do
    runningSessions=$(curl -s -u ${tcUser}:${tcPw} http://${host}:${port}/manager/text/sessions?path=/gwas/pussycat | grep sessions)
    if [[ ! -z $runningSessions && ! -f ${dataFolder}/${fileName} ]]; then 
        echo -n "."; 
        sleep 10m
    else
        echo -e "\n[Info] Pussycat sessions finished or file is ready."
        break
    fi
done
sleep 5m

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



