#!/usr/bin/env bash

##
## This script was written to replace the data export stage of the GWAS Catalog data release plan
## 
## List of exported files:
##  - Association file.
##  - Alternative association file.
##  - Study file.
##  - Alternative association file.
##  - Ancestry file.
##  - Trait mapping file.
##  - GWAS Catalog knowledge base file.
##  - GWAS Catalog diagram.
##  - Stats file generation
##  - Release report
##  - Readme file

# Workflow:
## 1 - Processing and testing command line parameters.
## 2 - Cleaning up output directory
## 3 - Extracting output files from tomcat
## 4 - Generate trait mapping file.
## 5 - Fetch owl file.
## 6 - Fetch diagram file + convert
## 7 - Generate release notes
## 8 - Generate stats file
## 9 - Extract release info (Ensembl mapping, dbSNP version, build)
##10 - Generate readme file.

# Generate date string:
export today=$(date "+%Y-%m-%d")

##
## Fetching applied Ensembl release, Genome build, dbSNP version:
##
function fetch_release_info {
    statsFile="${1}" # not tested, it is already ferified earlier:
    read genomeBuild dbSNPBuild EnsemblReles <<<$(cat $statsFile | perl -MData::Dumper -lane '@a = split "=", $_; $h{$a[0]} = $a[1]; END {printf "%s %s %s", $h{"genomebuild"}, $h{"dbsnpbuild"}, $h{"ensemblbuild"} }')

}

##
## This function fetches ancestry/association and study data from the solr index:
##
function fetch_data_from_tomcat {
    outputDir="${1}"
    host="${2}"

    # We need to test all the variables to make sure we have all of them
    if [[ -z "${3}" ]]; then 
        echo '[Error] To fetch data from tomcat, you have to pass the outputDir, host name, host port, and ensmebl release. Exiting.'
        exit 1;
    fi

    # Associative array to get proper file name:
    declare -A fileTypes=(
        ['association']="gwas-catalog-associations.tsv"
        ['alternative_assocation']="gwas-catalog-associations_ontology-annotated.tsv"
        ['study']="gwas-catalog-studies.tsv"
        ['alternative_study']="gwas-catalog-studies_ontology-annotated.tsv"
        ['ancestry']="gwas-catalog-ancestry.tsv"
    )

    # Associative array to get tomcat queries:
    declare -A queries=(
        ['association']="q=text:*&pvalfilter=&orfilter=&betafilter=&datefilter=&genomicfilter=&traitfilter[]=&dateaddedfilter=&facet=association"
        ['alternative_assocation']="q=text:*&pvalfilter=&orfilter=&betafilter=&datefilter=&genomicfilter=&traitfilter[]=&dateaddedfilter=&efo=true&facet=association"
        ['study']="q=text:*&pvalfilter=&orfilter=&betafilter=&datefilter=&genomicfilter=&traitfilter[]=&dateaddedfilter=&facet=study"
        ['alternative_study']="q=text:*&pvalfilter=&orfilter=&betafilter=&datefilter=&genomicfilter=&traitfilter[]=&dateaddedfilter=&efo=true&facet=study"
        ['ancestry']="q=text:*&pvalfilter=&orfilter=&betafilter=&datefilter=&genomicfilter=&traitfilter[]=&dateaddedfilter=&ancestry=true&facet=study"
    )

    echo "[Info] Fetching data from tomcat... "

    # Looping though all file types and fetch data from tomcat:
    for fileType in "${!fileTypes[@]}"; do

        fileName=${fileTypes[${fileType}]}
        query=${queries[${fileType}]}

        ##
        ## Generate file:
        ##
        echo -n "[Info] Fetching ${fileType//_/ } data... "
        curl -s -g -f "${host}/gwas/api/search/downloads?${query}" -o ${outputDir}/${fileName}

        # Test if the generation of the file was successful:
        if [[ ! -f ${outputDir}/${fileName} ]]; then
            echo -e "\n[Error] The generation of the association file (${fileName}) failed. Exiting."
            exit 1;
        else 
            echo "done."
        fi
    done
}


##
## This function calls the generation of the trait mapping file:
##
function generate_trait_mapping {
    outputDir="${1}"
    scriptDir="${2}"

    if [[ ! -d ${scriptDir} ]]; then
        echo "[Error] The provided script dir (${scriptDir}) is not a direactory. Exiting."
        exit 1;
    elif [[ ! -f ${scriptDir}/map-parents.sh ]]; then
        echo "[Error] The parent mapper application (map-parents.sh) could not be found. Exiting."
        exit 1;
    fi

    echo "[info] Generate trait mapping file..."
    ${scriptDir}/map-parents.sh -o ${outputDir}/gwas_catalog_trait-mappings_r${today}.tsv

    # Testing if the output file is successfully generated:
    if [[ ! -f ${outputDir}/gwas_catalog_trait-mappings_r${today}.tsv ]]; then
        echo "[Error] Generation of the trait mapping file failed. Exing."
        exit 1;
    fi
}


##
## Generate readme file:
##
function generate_readme {

    # Parameters:
    outputDir="${1}"
    genomeBuild="${2}"
    dbSNPBuild="${3}"
    ensemblRelease="${4}"

    # Get association files:
    assocFile=$( cd ${outputDir}; ls gwas_catalog_v1.0-associations* )
    assocAltFile=$( cd ${outputDir}; ls gwas_catalog_v1.0.2-associations* )

    # Get study files:
    studyFile=$( cd ${outputDir}; ls gwas_catalog_v1.0-studies* )
    studyAltFile=$( cd ${outputDir}; ls gwas_catalog_v1.0.2-studies* )

    # Get trait mapping file:
    traitMappingFile=$( cd ${outputDir}; ls gwas_catalog_trait-mappings* )

    # Get ancestry file:
    ancestryFile=$( cd ${outputDir}; ls gwas_catalog-ancestry* )

    # Generating the readme text:
    echo "This directory contains downloadable GWAS catalog files.

GWAS catalog release date: ${today}
Ensembl release version that the data is mapped to: e${ensemblRelease}
The applied genome build: ${genomeBuild}
dbSNP build: ${dbsnpbuild}

Directory contains:

    ${assocFile}   - All associations without ontology terms
    ${assocAltFile} - All associations with added ontology annotations and GWAS Catalog study accession numbers

    ${studyFile}       - All studies 
    ${studyAltFile}     - All studies with added ontology annotations and GWAS Catalog study accession numbers

    ${ancestryFile}               - Sample size and population information for all studies.

    ${traitMappingFile}       - A file describing the mapping between the reported traits in the GWAS Catalog and EFO traits

    gwas-diagram.svg/png - The famous diagram representation of the GWAS catalog in various formats
    

    Each release of the GWAS Catalog is also available as an OWL knowledge base that can be loaded into an RDF triple store. 
    In order to work with the knowledge base, a copy of the schema ontology and of the Experimental Factor Ontology (EFO) are required. 
    For more information on our use of ontologies, see our ontology page (https://www.ebi.ac.uk/gwas/docs/ontology): 

    gwas-kb.owl       - The GWAS Catalog knowledge base in web ontology language
    gwas-diagram.owl  - Schema ontology

    release_notes.txt - a file reporting the changes in the current release.

For more information on the file headers: https://www.ebi.ac.uk/gwas/docs/fileheaders

Further downloads: https://www.ebi.ac.uk/gwas/docs/file-downloads
Further documentation: https://www.ebi.ac.uk/gwas/docs
Ontology page: https://www.ebi.ac.uk/gwas/docs/ontology

MD5 sums:" > "${outputDir}/README.txt"

    # Looping through all the files and generate md5 sums:
    for file in ${outputDir}/*; do
        if [[ $file == "${outputDir}/README.txt" ]]; then continue; fi
        echo "     $(md5sum "${file}" | cut -f1 -d" ") - $(basename ${file})" >> "${outputDir}/README.txt"
    done

    # Adding a blank line at the end of the file:
    echo >> "${outputDir}/README.txt"

}

##
## Generate help message:
##
function display_help {
    echo "Data exported script."
    echo " "
    echo "Usage: $0 -o <output folder> \\"
    echo "          -e <Ensembl version> \\"
    echo "          -s <mapper folder> \\"
    echo "          -x <tomcat host> \\"
    echo "          -k <knowledge base folder> \\"
    echo "          -d <diagram folder> \\"
    echo "          -r <release file> \\"
    echo "          -h"
    echo " "
    echo "Where:"
    echo "      <output folder>   : directory in which the exported files will be generated."
    echo "      <Ensembl version> : the Ensembl version on which the data is mapped."
    echo "      <mapper folder>   : where the parent mapper application is hosted."
    echo "      <tomcat host>     : the server on which the gwas appliation is running with port."
    echo "      <knowledge base folder> : Folder where the .owl knowledge base files are stored."
    echo "      <diagram folder>        : folders where the diagrams generated."
    echo "      <release file>          : file with the release notes."
    echo " "
    echo " "

    exit 1;
}


##
## Handling command line parameters
##
OPTIND=1
while getopts "ho:x:e:s:k:d:r:" opt; do
    case "$opt" in
        'o' ) outputDir=${OPTARG} ;;
        'x' ) host=${OPTARG} ;;
        'e' ) ensemblRelease=${OPTARG} ;;
        's' ) scriptDir=${OPTARG} ;;
        'k' ) knowledgeBaseDir=${OPTARG} ;;
        'd' ) diagramDir=${OPTARG} ;;
        'r' ) releaseFile=${OPTARG} ;;
        'h' | * ) display_help ;;
    esac
done


# Run script:
echo "[Info] Data export script is called on: ${today}"

# Test output dir:
if [[ -z "${outputDir}" ]]; then
    echo "[Error] The output directory needs to be specified. Exiting."
    exit 1;
elif [[ ! -d "${outputDir}" ]]; then
    echo "[Error] The provided output directory (${outputDir}) is not a directory. Exiting."
    exit 1;
fi

# Test scritp dir:
if [[ -z "${scriptDir}" ]]; then
    echo "[Error] The mapping application is not specified. Exiting."
    exit 1;
elif [[ ! -d "${scriptDir}" ]]; then 
    echo "[Error] The provided directory for the parent mapping application (${scriptDir}) does not exists. Exiting."
    exit 1;
fi

# Test ensembl release:
if [[ -z "${ensemblRelease}" ]]; then
    echo "[Error] Ensembl release is not specified. Exiting."
    exit 1;
fi

# Test host:
if [[ -z "${host}" ]];then 
    echo "[Error] Tomcat host is not specified. Exiting."
    exit 1;
fi 

# Test virtuoso directory:
if [[ -z "${knowledgeBaseDir}" ]]; then
    echo "[Error] Virtuoso folder needs to be specified. Exiting."
    exit 1;
elif [[ ! -d "${knowledgeBaseDir}" ]]; then
    echo "[Error] The provied virtuoso folder ($knowledgeBaseDir) is not a folder. Exiting."
    exit 1;
fi

# Test diagramdir:
if [[ -z "${diagramDir}" ]]; then
    echo "[Error] Diagram folder needs to be specified. Exiting."
    exit 1;
elif [[ ! -d "${diagramDir}" ]]; then
    echo "[Error] The provied Diagram folder ($diagramDir) is not a folder. Exiting."
    exit 1;
fi

# Test release notes dir:
if [[ -z "${releaseFile}" ]]; then
    echo "[Error] Release folder is not specified. Exiting."
    exit 1;
elif [[ ! -f "${releaseFile}" ]]; then
    echo "[Error] The provided release folder is not specified. Exiting."
    exit 1;
fi

# Test retrieval of the gwas page:
wget -q ${host}/gwas --timeout 30 -O - 2>/dev/null >/dev/null

if [[ $? != 0 ]]; then 
    echo "[Error] The specified host ($host) is down. Exiting."
    exit 1;
fi

# Print out report:
echo "[Info] Applied host: ${host}"
echo "[Info] Parent mapper application folder: ${scriptDir}"
echo "[Info] Output folder: ${outputDir}"
echo "[Info] Diagram directory: ${diagramDir}"
echo "[Info] Virtuso directory: ${knowledgeBaseDir}"
echo "[Info] Release notes copyed from ${releaseFile}"
echo " "

##
## Parameters look alright. 
##

# Cleaning up the output directory:
echo "[Info] Cleaning up output directory..."
rm -rf ${outputDir}/*

# Generate files extracted from tomcat:
fetch_data_from_tomcat "${outputDir}" "${host}" "${ensemblRelease}"

# Generate trait mapping file:
generate_trait_mapping "${outputDir}" "${scriptDir}"

# Fetch owl files:
echo "[Info] Copying owl files from virtuoso folder."
cp "${knowledgeBaseDir}/gwas-diagram.owl" "${outputDir}/gwas-diagram.owl"
cp "${knowledgeBaseDir}/gwas-kb.nightly.owl" "${outputDir}/gwas-kb.owl"

if [[ ! -f "${outputDir}/gwas-diagram.owl" ]]; then
    echo "[Error] Failed to copy gwas-diagram.owl. Exiting." 
    exit 1;
elif [[ ! -f "${outputDir}/gwas-kb.owl" ]]; then
    echo "[Error] Failed to copy gwas-kb.owl. Exiting."
    exit 1;
fi

# Fetch svg file:
echo "[Info] Copying diagram file."
cp "${diagramDir}/4FF04FDA193DF9FBCB6333FD8AEC0BD6F29EA0D4.svg" "${outputDir}/gwas-diagram.svg"

if [[ ! -f "${outputDir}/gwas-diagram.svg" ]]; then
    echo "[Error] Failed to copy diagram file. Exiting."
    exit 1;
fi

# Convert svg file:
echo "[Info] converting diagram svg to png."
convert -background white -density 350 -resize "3500x" "${outputDir}/gwas-diagram.svg" "${outputDir}/gwas-diagram.png"

if [[ $? != 0 ]]; then
    echo "[Error] Converting svg diagram to png failed. Exiting."
    exit 1;
fi

# Fetch release notes:
cp "${releaseFile}" "${outputDir}"
if [[ ! -f "${outputDir}/release_notes.txt" ]]; then 
    echo "[Error] Failed to copy relese notes. Exiting."
    exit 1;
fi




##
## 1. Generate stats file:
##


##
## Fetch release info from stats file:
##
read genomeBuild dbSNPBuild EnsemblReles <<<$(cat $statsFile \
    | perl -MData::Dumper -lane '@a = split "=", $_; $h{$a[0]} = $a[1]; END {printf "%s %s %s", $h{"genomebuild"}, $h{"dbsnpbuild"}, $h{"ensemblbuild"} }')


##
## Generate readme file:
##

generate_readme  "${outputDir}" "${genomeBuild}" "${dbSNPBuild}" "${EnsemblReles}"