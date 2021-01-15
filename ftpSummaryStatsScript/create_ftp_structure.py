#summary_statistics
#+-- gcst001-gcst002
#|   +-- gcst001
#|   +-- gcst002
#+-- gcst003-gcst004
#|   +-- gcst003
#|   +-- gcst004
#+-- gcst005-gcst006
#|   +-- gcst005
#+-- gcst...(left to preserve paths)
#+-- author_pmid_gcst...(left to preserve paths)

import os
import glob
import re
import numpy as np

ftp_base = "staging"
range_size = 1000

sumstats = glob.glob(os.path.join(ftp_base, '*GCST*'))

def get_gcst_range(gcst):
    number_part = int(gcst.split("GCST")[1])
    floor = int(np.fix(number_part / range_size) * range_size) + 1
    upper = floor + (range_size -1)
    range_str = "GCST{f}-GCST{u}".format(f=str(floor), u=str(upper))
    return range_str


# get gcst
for f in sumstats:
    gcst = None
    basename = os.path.basename(f)
    gcst_regex = re.search(r'GCST[0-9]+', basename)
    gcst = gcst_regex.group(0) if gcst_regex else None
    if gcst:
        print(gcst)
        print(get_gcst_range(gcst))
    else:
        print("Couldn't find a GCST in {}".format(basename))


#for d in pub
# get gcst_range

# mv dir to gcst_range/gcst

# create symlink where it was

