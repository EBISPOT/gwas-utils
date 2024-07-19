#!/bin/bash

md5file="md5sums.txt"

# Get list of files from md5sums.txt
md5_files=$(cut -d' ' -f3 "$md5file")

mismatch_found=0

# Check if all files in md5sums.txt exist in the directory
for file in $md5_files; do
    if [ ! -f "$file" ]; then
        echo "File listed in $md5file but missing in directory: $file"
        mismatch_found=1
    fi
done

# Check if all files in the directory are listed in md5sums.txt
for file in $(ls -A); do
    if ! grep -q "$file" "$md5file"; then
        echo "File in directory not listed in $md5file: $file"
        mismatch_found=1
    fi
done

if [ $mismatch_found -eq 0 ]; then
    echo "All files match bijectively with $md5file."
else
    echo "There are mismatches between the files in the directory and $md5file."
fi
