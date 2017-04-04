#!/usr/bin/env python3

import argparse
from os.path import isfile
from math import ceil

AVAILABLE_FRAMES = 512

class Program:
    def __init__(self, prog_no, prog_size, pages_needed, start_loc):
        self.prog_no = prog_no
        self.prog_size = prog_size
        self.pages_needed = pages_needed
        self.start_loc = start_loc
        self.end_loc = start_loc + pages_needed - 1 # starting from 0, hence -1

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
    parser.add_argument("page_size", type=int, choices=[2**i for i in range(5)], help="page size")
    parser.add_argument("algorithm", choices=["clock", "fifo", "lru"], help="page replacement algorithm")
    parser.add_argument("paging", type=int, choices=[0, 1], help="demand/prepaging")

    args = parser.parse_args()

    with open(args.programlist) as f:
        # index == prog number. filter blank lines
        programlist = [int(line.split()[1]) for line in f if line.strip()]

    page_tables = create_page_tables(programlist, args.page_size)
    print_page_tables(page_tables, args.page_size)

def create_page_tables(programlist, page_size):
    page_tables = []
    abs_page_loc = 0

    for prog_no, prog_size in enumerate(programlist):
        pages_needed = ceil(prog_size / page_size)
        page_tables.append(Program(prog_no, prog_size, pages_needed, abs_page_loc))
        abs_page_loc += pages_needed

    return page_tables

def print_page_tables(page_tables, page_size):
    print("{}\t{}\t{}\t{}\t{}".format("no", "size", "page", "need", "loc"))
    for p in page_tables:
        print("{}\t{}\t{}\t{}\t{} - {}".format(p.prog_no, p.prog_size, page_size, p.pages_needed, p.start_loc, p.end_loc))

if __name__ == "__main__":
    main()
