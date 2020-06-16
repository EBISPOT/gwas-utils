import getopt
import math
import os
import re
import statistics
import sys


def get_build_stats(inputdir):
    lines = dict()
    for fname in os.listdir(inputdir):
        path = os.path.join(inputdir, fname)
        if os.path.isdir(path):
            with open(path + "/" + fname + ".o") as file_in:
                for line in file_in:
                    if "Run time" in line:
                        lines[fname] = int(re.split(" +", line)[4])
    print(lines)
    print("median: " + str(statistics.median(lines.values())))
    print("mean: " + str(statistics.mean(lines.values())))
    values = list(lines.values())
    keys = list(lines.keys())
    maxTime = max(lines.values())
    maxValue = values.index(maxTime)
    maxValue = keys[maxValue]
    print("max: " + maxValue + " in " + str(maxTime))
    minTime = min(lines.values())
    minValue = values.index(minTime)
    minValue = keys[minValue]
    print("min: " + minValue + " in " + str(minTime))
    return

if __name__ == '__main__':
    #search all output logs,
    #find "Run time"
    #print top 10 run times
    #print average, median, mode

    inputdir = "."
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hd:", ["base_dir="])
    except getopt.GetoptError:
        print('unpublished_study_export.py -d <base dir>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('unpublished_study_export.py -d <base dir>')
            sys.exit()
        elif opt in ("-d", "--base_dir"):
            inputdir = arg
    get_build_stats(inputdir)
