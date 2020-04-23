import argparse
from datetime import datetime
import os

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='This script compares the last modified time between two files')
    parser.add_argument('--f1', type = str, required=True, help = 'Filename 1.')
    parser.add_argument('--f2', type = str, required=True, help = 'Filename 2.')
    args = parser.parse_args()
    last_modified_date_one = datetime.fromtimestamp(os.path.getmtime(args.f1))
    last_modified_date_two = datetime.fromtimestamp(os.path.getmtime(args.f2))
    timedelta = last_modified_date_one - last_modified_date_two
    print(int(timedelta.total_seconds() / 60),  ' minutes')
