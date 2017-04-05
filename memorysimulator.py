#!/usr/bin/env python3

import queue
import argparse
import math
from os.path import isfile
from pprint import pprint

AVAILABLE_FRAMES = 512
page_file_size = 0
timer = 0 # an upcounting variable used for remove last refrence

class Program:
    def __init__(self, number, size, pages_needed, start_loc):
        self.number = number
        self.size = size
        self.pages_needed = pages_needed
        self.start_loc = start_loc
        self.end_loc = start_loc + pages_needed - 1 # starting from 0, hence -1

clockloc = 0 # where the clock is in it's cycle
queue = queue.Queue()

class Progpage:
    def __init__(self, prognum, relprogpage, location, usebit, tsr):
        self.prognum = prognum
        self.relprogpage = relprogpage
        self.location = location
        self.usebit = usebit  #for clock alogorithm
        self.tsr = tsr #for remove last used

def create_page_tables(programlist, page_size):
    page_tables = []
    abs_page = 0

    for i, prog_size in enumerate(programlist):
        pages_needed = (prog_size // page_size) + 1
        page_tables.append(Program(i, prog_size, pages_needed, abs_page))
        abs_page += pages_needed

    return page_tables

def create_mem(program_tables):
    mem_table = []
    page_file_size = AVAILABLE_FRAMES / page_size
    page_per_program = page_file_size // len(program_tables)
    for prognum in range(0, len(program_tables)):
        for y in range(0, int(page_per_program)):
            mem_table.append(Progpage(prognum, y ,program_tables[prognum].start_loc + y, 1, 0))
    return mem_table

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
    parser.add_argument("algo", choices=["clock", "fifo", "lru"], help="page replacement algorithm")
    parser.add_argument("paging", type=int, choices=[0, 1], help="demand/prepaging")

    args = parser.parse_args()

	#makes args into global vars
    global page_size, algo, paging
    page_size = args.page_size
    algo = args.algo
    paging = args.paging
    
    with open(args.programlist) as f:
        # index == prog number. filter blank lines
        programlist = [int(line.split()[1]) for line in f if line.strip()]

	#test code for 
    page_tables = create_page_tables(programlist, args.page_size)
    print_page_tables(page_tables, args.page_size)
    
	#test code for the main memory table
    mem_table = create_mem(page_tables)
    print_mem_table(mem_table)

def print_page_tables(page_tables, page_size):
    print("{}\t{}\t{}\t{}\t{}".format("no", "size", "page", "need", "loc"))
    for p in page_tables:
        print("{}\t{}\t{}\t{}\t{} - {}".format(p.number, p.size, page_size, p.pages_needed, p.start_loc, p.end_loc))

def print_mem_table(page_tables):
    print("{}\t{}\t{}\t{}\t{}".format("program", "rel loc", "loc", "usebit", "active clocks"))
    for p in page_tables:
        print("{}\t{}\t{}\t{}".format(p.prognum, p.relprogpage, p.location, p.usebit, p.tsr))

if __name__ == "__main__":
    main()