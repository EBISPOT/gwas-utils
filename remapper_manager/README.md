# GWAS Catlog Remapper manager

Each time Ensembl releases a new version, we have to remap the entire catalog to the new version. The remapping is initiated by removing certain values from the database which triggers remapping when the mapper application of the [goci](http://github.com/EBISPOT/goci) repo is initiated. As the remapping process takes a long time and blocks the database, we have to call the remapper for small chunks approximately 10k associations at a time outside curators' working hours. This repo contains scripts to automate the database update. 

The progression is saved into a json file, so when called next time, it can continue.

## Usage

`python ./remapper.py --dbInstanceName ${instance} --progressFileName ${progressFile} --remapCount ${count}`

Where `instance` is the database name (`dev2` is the default), `progressFileName` is the json file that contains information on the progression, `count` the number of associations newly added to the queue. 

