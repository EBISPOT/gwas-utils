import getopt
import sys


def compare_diagrams(src_file, tgt_file):
    src_lines = open(src_file, encoding='UTF-8').read().splitlines()
    tgt_lines = open(tgt_file, encoding='UTF-8').read().splitlines()
    ab_match = 0
    ba_match = 0
    a_not_b = []
    b_not_a = []
    for src_line in src_lines:
        if src_line in tgt_lines:
                ab_match += 1
        else:
            a_not_b.append(src_line)

    for tgt_line in tgt_lines:
        if tgt_line in src_lines:
                ba_match += 1
        else:
            b_not_a.append(tgt_line)
    print("searched " + str(len(src_lines)))
    print("matches " + str(ab_match) + ", " + str(ba_match))
    print("differences " + str(len(a_not_b)) + ", " + str(len(b_not_a)))
    for e in a_not_b:
        print("<<< " + e)
    for e in b_not_a:
        print(">>> " + e)
    return


if __name__ == '__main__':
    src_file = "C:/Users/jstewart/Documents/svg_cache/4FF04FDA193DF9FBCB6333FD8AEC0BD6F29EA0D4.svg"
    tgt_file = "C:/Users/jstewart/Documents/svg_cache/new/4FF04FDA193DF9FBCB6333FD8AEC0BD6F29EA0D4.svg"
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hs:t:", ["src_file=", "tgt_file="])
    except getopt.GetoptError:
        print('unpublished_study_export.py -s <src_file> -t <tgt_file>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('unpublished_study_export.py -s <src_file> -t <tgt_file>')
            sys.exit()
        elif opt in ("-s", "--src_file"):
            src_file = arg
        elif opt in ("-t", "--tgt_file"):
            tgt_file = arg
    compare_diagrams(src_file, tgt_file)
