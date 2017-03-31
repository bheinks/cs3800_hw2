#!/usr/bin/env python3

import argparse
from os.path import isfile

# argparse "type" to determine if a file exists
def file_exists(filename):
    if not isfile(filename):
        raise argparse.ArgumentTypeError("{} does not exist".format(filename))
    return filename

def main():
    parser = argparse.ArgumentParser(description = "Simulate a virtual memory management system with various page sizes, paging replacement algorithms, and demand/prepaging.")

    # argparse performs all of the necessary checks on input formatting
    parser.add_argument("programlist", type=file_exists)
    parser.add_argument("programtrace", type=file_exists)
    parser.add_argument("page size", type=int, choices=[2**i for i in range(5)])
    parser.add_argument("page replacement algorithm", choices=["clock", "fifo", "lru"])
    parser.add_argument("demand/prepaging", type=int, choices=[0, 1])

    args = parser.parse_args()

if __name__ == "__main__":
    main()
