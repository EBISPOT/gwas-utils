# Wrapper for pussycat

Upon data release a step is dedicated to generate the GWAS Catalog diagram for the new data. Unfortunately as the dataset was growing this step was keep failing. This script was written to resolve this issue by observing the progression of the file generation and pussycat session.

### What it does

* Once the script is called it looks up the expected file in the data directory and if that exists it checks the md5sum and backs up the file.
* Then calls pussycat with the hardcoded parameters.
* Then keeps watching the data directory for the appearance of new file.
* If the file is there OR there is no running pussycat instance on the defined host, the script progresses.
* If there's a file it checks if it is indeed an svg, checks the number of associations, chromosomes.
* If there was old diagram file, it compares the md5 sum.
* The exit code is only zero if proper svg file is generated, otherwise the exit code is 1
* If the new file is the same as the old, the exit code is 0, but warning is given.

### Usage

```bash
./pussycat_caller.sh ${host} ${port} ${dataDir} ${tomcatUser} ${tomcatPasswd}
```
Where `dataDir` is the folder where the pussycat application saves the svg (svg_cache folder). The tomcat credentials are requierd to check for running pussycat sessions.


### More information

For more information see [confluence page](https://www.ebi.ac.uk/seqdb/confluence/display/GOCI/Diagram+generator).


