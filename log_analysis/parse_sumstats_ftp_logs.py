import sys
import argparse
import pandas as pd

"""
Script for parsing the FTP logs from meter.

"""


pd.set_option('display.max_colwidth', None)


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-f",
                           help='The path to the summary statistics ftp log csv',
                           required=True)
    argparser.add_argument("-min",
                           help='Minimum Bytes to be considered a valid sumstats file, default is 1000000',
                           required=False,
                           default=1000000)

    args = argparser.parse_args()

    df = pd.read_csv(args.f, header=0, names=['resource', 'file_size', 'count'], dtype={"resource": str})

    df = df[df.file_size > int(args.min)]
    print(df.resource)
    df.resource = df.resource.str.replace('/pub/databases/gwas/summary_statistics/','')
    df = df.drop(columns=['file_size'])


    raw = df[~df.resource.str.contains('harmonised')]
    raw.resource = raw.resource.str.replace('/.*','')
    raw = raw.groupby('resource').agg('max')

    f_and_h = df[df.resource.str.contains('harmonised')]

    formatted = f_and_h[f_and_h.resource.str.contains('\.f\.')]
    formatted = formatted.groupby('resource').agg('max')

    harmonised = f_and_h[f_and_h.resource.str.contains('\.h\.')]
    harmonised = harmonised.groupby('resource').agg('max')

    raw_total = raw['count'].sum()
    f_total = formatted['count'].sum()
    h_total = harmonised['count'].sum()

    df = df.groupby('resource').agg('max')
    top_all = df.sort_values(by=["count"], ascending=False).head(10)
    top_raw = raw.sort_values(by=["count"], ascending=False).head(10)
    top_f = formatted.sort_values(by=["count"], ascending=False).head(10)
    top_h = harmonised.sort_values(by=["count"], ascending=False).head(10)

    print("Stats:")
    print("raw total: {}".format(str(raw_total)))
    print("formatted total: {}".format(str(f_total)))
    print("harmonised total: {}".format(str(h_total)))
    print("complete total: {}".format(str(sum([raw_total, f_total, h_total]))))
    print("\n========================\n")

    print("top downloads:")
    print(top_all)

    print("\ntop raw:")
    print(top_raw)

    print("\ntop formatted:")
    print(top_f)

    print("\ntop harmonised:")
    print(top_h)

    df.sort_values(by=["count"], ascending=False).to_csv("all.csv")
    raw.sort_values(by=["count"], ascending=False).to_csv("raw.csv")
    formatted.sort_values(by=["count"], ascending=False).to_csv("f.csv")
    harmonised.sort_values(by=["count"], ascending=False).to_csv("h.csv")


if __name__ == '__main__':
    main()