# Reported Traits

## Description: 
This script is desiged for curators to be able to get a file of all existing reported traits from the database, analyze a file of curator provided reported traits to find existing similar reported traits in the database, and to be able to submit a batch of reported traits into the database.
(Status as of Aug 2020)

## Usage
`./wrapper.sh -d DATABASE_ALIAS -a dump`

The `-a` action options are:
- `-a dump` - creates a file of all existing reported traits from the database. The file is saved at the location the script is run and is named "reported_trait.csv"
- `-a analyze` - reads in a text file of reported traits, analyzes each trait against all existing traits in the database, and then saves the results as a file in the location the script is run named "similarity_analysis_results.csv"
- `-a upload` - reads in a text file of reported traits and loads these into the database

NOTE: See specific location of wrapper.sh on the [GWAS Confluence page](https://www.ebi.ac.uk/seqdb/confluence/display/GOCI/Script+to+Manage+Reported+Traits)