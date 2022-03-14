# Association Filter

This application flags peak associations in a distance based fashion.

## Usage

1. Activate virtual env:

```bash
source ${scriptDir}/.env/bin/activate
```

2. Call script:

```bash
${scriptDir}/peak_finder.py -f test.input.txt -o test.output.txt -t 1e-2 -w 100000 -p
```

Where:

* **-f**: input table in tsv format. (required)
* **-o**: output file name, saved in the same format. (required)
* **-w**: window size (default 100kb)
* **-t**: p-value threshold above which association's won't be considered as peaks. (default: `1e-5`)
* **-p**: turning pruning on: associations below the significance threshold will be removed from the output

### Input file example:

```
RS_ID       pvalue    chromosome  bp_location
rs1260326   1.00E-09  2           27730940
rs780094    1.40E-10  2           27741237
rs780093    1.50E-10  2           27742603
rs13431652  3.80E-11  2           169753415
rs1402837   1.80E-08  2           169757354
rs573225    1.20E-11  2           169757541
rs560887    3.00E-13  2           169763148
rs563694    1.60E-13  2           169774071
rs537183    1.50E-13  2           169774646
```
The above column labels are required and the script will fail if any of them is not present. Other columns will be ignored, but will be included in the output file.

### Output example:

```
RS_ID       pvalue    chromosome  bp_location  isTopAssociation
rs1260326   1.00E-09  2           27730940     false
rs780094    1.40E-10  2           27741237     true
rs780093    1.50E-10  2           27742603     false
rs13431652  3.80E-11  2           169753415    false
rs1402837   1.80E-08  2           169757354    false
rs573225    1.20E-11  2           169757541    false
rs560887    3.00E-13  2           169763148    false
rs563694    1.60E-13  2           169774071    false
rs537183    1.50E-13  2           169774646    false
```

The output table will contain a column called `isTopAssociation` telling if it is a top association or not. An association is considered as top associaiton if the p-value is below the significance threshold (1e-5 by default), and there's no association with lower p-value within the defined window (100kbp by default.) This flag is set to `REQUIRES REVIEW` if two or more associaiton has the same lowest p-value in a region and programatically it is not possible to make a distinction. And the curators will have to make the call. The script handles very low p-values below 1e-308 with avoiding underflow error. 

If pruning is turned on with the `-p` switch, the output file won't contain associations below the p-value threshold for increased clearaty. 

## Requirement

See `requirements.txt` for the list of python packages used by the application.

