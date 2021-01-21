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
import shutil


#full path required
ftp_base = ""
range_size = 1000

sumstats = glob.glob(os.path.join(ftp_base, '*GCST*'))

def get_gcst_range(gcst):
    number_part = int(gcst.split("GCST")[1])
    floor = int(np.fix(number_part / range_size) * range_size) + 1
    upper = floor + (range_size -1)
    range_str = "GCST{f}-GCST{u}".format(f=str(floor).zfill(6), u=str(upper).zfill(6))
    return range_str


# get gcst
for f in sumstats:
    gcst = None
    basename = os.path.basename(f)
    gcst_regex = re.search(r'GCST[0-9]+', basename)
    gcst = gcst_regex.group(0) if gcst_regex else None
    if gcst:
        print(gcst)
        gcst_range = get_gcst_range(gcst)
        new_dir = os.path.join(ftp_base, gcst_range, gcst)
        # move dir
        shutil.move(f, new_dir)
        # create symlink
        os.symlink(new_dir, f, target_is_directory=True)
    else:
        print("Couldn't find a GCST in {}".format(basename))
