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

class Progpage:
    def __init__(self, index, prog_no, relprogpage, location, usebit, tsr):
        self.index = index
        self.prog_no = prog_no
        self.relprogpage = relprogpage
        self.location = location
        self.usebit = usebit # for clock alogorithm
        self.tsr = tsr # for remove last used

def main(pl_filename, pt_filename, page_size, algorithm, paging):
    with open(pl_filename) as f:
        # index == prog number. filter blank lines
        programlist = [int(line.split()[1]) for line in f if line.strip()]

    with open(pt_filename) as f:
        pass
        #programtrace = [(int(i) for i in line.split()) for line in f if line.strip()]

    page_tables = create_page_tables(programlist, page_size)
    print_page_tables(page_tables, page_size)

    print()
    
    # test code for the main memory table
    mem_table = create_mem(page_tables, page_size)
    print_mem_table(mem_table)
    #print(programtrace)

#create program index files
def create_page_tables(programlist, page_size):
    page_tables = []
    abs_page = 0

    for i, prog_size in enumerate(programlist):
        pages_needed = ceil(prog_size / page_size)
        page_tables.append(Program(i, prog_size, pages_needed, abs_page))
        abs_page += pages_needed

    return page_tables

#create and allocate main memory
def create_mem(page_tables, page_size):
    mem_table = []
    page_file_size = AVAILABLE_FRAMES / page_size
    page_per_program = int(page_file_size // len(page_tables))
    index = 0

    for program in page_tables:
        for page in range(page_per_program):
            mem_table.append(Progpage(index, program.prog_no, page, program.start_loc + page, 1, 0))
            index += 1

    return mem_table

# first in first out algorithm
def fifo():
    return

# clock algorithm
def clock():
    return

# last recently used algorithm
def lru():
    return

def print_page_tables(page_tables, page_size):
    print("{}\t{}\t{}\t{}\t{}".format("no", "size", "page", "need", "loc"))
    for p in page_tables:
        print("{}\t{}\t{}\t{}\t{} - {}".format(p.prog_no, p.prog_size, page_size, p.pages_needed, p.start_loc, p.end_loc))

def print_mem_table(mem_table):
    print("{}\t{}\t{}\t{}\t{}".format("program", "rel loc", "loc", "usebit", "active clocks"))
    for p in mem_table:
        print("{} {}\t{}\t{}\t{}".format(p.index, p.prog_no, p.relprogpage, p.location, p.usebit, p.tsr))

# argparse "type" to determine if a file exists
def file_exists(filename):
    if not isfile(filename):
        raise argparse.ArgumentTypeError("{} does not exist".format(filename))

    return filename

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Simulate a virtual memory management system with various page sizes, paging replacement algorithms, and demand/prepaging.")

    # argparse performs all of the necessary checks on input formatting
    parser.add_argument("programlist", type=file_exists, help="programlist file")
    parser.add_argument("programtrace", type=file_exists, help="programtrace file")
    parser.add_argument("page_size", type=int, choices=[2**i for i in range(5)], help="page size")
    parser.add_argument("algorithm", choices=["clock", "fifo", "lru"], help="page replacement algorithm")
    parser.add_argument("paging", type=int, choices=[0, 1], help="demand/prepaging")

    args = parser.parse_args()
    main(args.programlist, args.programtrace, args.page_size, args.algorithm, args.paging)
