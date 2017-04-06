#!/usr/bin/env python3

import queue
import argparse
import math
from os.path import isfile
from math import ceil

AVAILABLE_FRAMES = 512
page_file_size = 0


class Program:
    def __init__(self, prog_no, prog_size, pages_needed, start_loc):
        self.prog_no = prog_no
        self.prog_size = prog_size
        self.pages_needed = pages_needed
        self.start_loc = start_loc
        self.end_loc = start_loc + pages_needed - 1 # starting from 0, hence -1

class Progpage:
    def __init__(self, ind, prognum, relprogpage, location, usebit, clocks):
        self.ind = ind
        self.prognum = prognum
        self.relprogpage = relprogpage
        self.location = location
        self.usebit = usebit  #for clock alogorithm
        self.clocks = clocks #for remove last used

#create program index files
def create_page_tables(programlist, page_size):
    page_tables = []
    abs_page = 0

    for i, prog_size in enumerate(programlist):
        pages_needed = (prog_size // page_size) + 1
        page_tables.append(Program(i, prog_size, pages_needed, abs_page))
        abs_page += pages_needed

    return page_tables

#create and allocate main memory
def create_mem(program_tables, timer):
    i = 0
    mem_table = []
    page_file_size = AVAILABLE_FRAMES / page_size
    page_per_program = page_file_size // len(program_tables)
    for prognum in range(0, len(program_tables)):
        for y in range(0, int(page_per_program)):
            mem_table.append(Progpage(i, prognum, y ,program_tables[prognum].start_loc + y, 1, timer))
            i += 1
            timer += 1
    return mem_table

# argparse "type" to determine if a file exists
def file_exists(filename):
    if not isfile(filename):
        raise argparse.ArgumentTypeError("{} does not exist".format(filename))
    return filename

#First in first out algorithm
def fifo(sim, mem_table):
    fifo_queue = queue.Queue()  #Queue for FiFo
    for x in range(0, len(sim)):
        for y in range(0, len(mem_table)):
            if sim[x][0] == mem_table[y].prognum and sim[x][1] == memtable[y].relprogpage:
                continue
            else:
                pass     
    return
#Clock algorithm
#def Clock():
#    return

#Last recently used algorithm
#def LRU():
#    return

def main():
    timer = 0 # an upcounting variable used for remove last refrence

    parser = argparse.ArgumentParser(description = "Simulate a virtual memory management system with various page sizes, paging replacement algorithms, and demand/prepaging.")

    # argparse performs all of the necessary checks on input formatting
    parser.add_argument("programlist", type=file_exists)
    parser.add_argument("programtrace", type=file_exists)
    parser.add_argument("page_size", type=int, choices=[2**i for i in range(5)], help="page size")
    parser.add_argument("algorithm", choices=["clock", "fifo", "lru"], help="page replacement algorithm")
    parser.add_argument("paging", type=int, choices=[0, 1], help="demand/prepaging")

    args = parser.parse_args()

	#makes args into global vars
    global page_size, algo, paging
    page_size = args.page_size
    algo = args.algorithm
    paging = args.paging
    
    with open(args.programlist) as f:
        # index == prog number. filter blank lines
        programlist = [int(line.split()[1]) for line in f if line.strip()]

    sim = []

    with open(args.programtrace) as f:
        for line in f:
            if line.strip():
                sim.append(line.split())

    

	#test code for 
    page_tables = create_page_tables(programlist, args.page_size)
    print_page_tables(page_tables, args.page_size)
    
	#test code for the main memory table
    mem_table = create_mem(page_tables, timer)
    print_mem_table(mem_table)

#Print fuctions for testing
def print_page_tables(page_tables, page_size):
    print("{}\t{}\t{}\t{}\t{}".format( "no", "size", "page", "need", "loc"))
    for p in page_tables:
        print("{}\t{}\t{}\t{}\t{} - {}".format(p.prog_no, p.prog_size, page_size, p.pages_needed, p.start_loc, p.end_loc))

def print_mem_table(page_tables):
    print("\t{}\t{}\t{}\t{}\t{}\t{}".format("index","program", "rel loc", "loc", "usebit", "clocks"))
    for p in page_tables:
        print("\t{}\t{}\t{}\t{}\t{}\t{}".format(p.ind, p.prognum, p.relprogpage, p.location, p.usebit, p.clocks))

if __name__ == "__main__":
    main()