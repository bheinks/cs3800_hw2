#!/usr/bin/env python3

import argparse
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

class Lookup:
    def __init__(self, prog_num, page_num, file_num):
        self.prog_num = prog_num
        self.page_num = page_num
        self.file_num = file_num

class Memory:
    def __init__(self, ind, prognum, page_num, usebit, clocks):
        self.ind = ind
        self.prognum = prognum
        self.page_num = page_num
        self.usebit = usebit  #for clock alogorithm
        self.clocks = clocks #for remove last used

#create program index files
def create_page_tables(programlist, page_size):
    page_tables = []
    abs_page = 0

    for i, prog_size in enumerate(programlist):
        pages_needed = ceil(prog_size / page_size)
        page_tables.append(Program(i, prog_size, pages_needed, abs_page))
        abs_page += pages_needed

    return page_tables

#create program tables
def create_prog_tables(page_tables):
    prog_tables = []
    for x in range(0, len(page_tables)):
        i = 0
        for y in range(0, page_tables[x].pages_needed):
            
            for z in range(0, int(page_size)):
                prog_tables.append(Lookup(x, y, i))
                i += 1
    return prog_tables

#create and allocate main memory
def create_mem(program_tables, timer, page_file_size):
    i = 0
    mem_table = []
    page_per_program = page_file_size // len(program_tables)
    for prognum in range(0, len(program_tables)):
        for y in range(0, int(page_per_program)):
            timer += 1
            mem_table.append(Memory(i, prognum, y, 1, timer))
            i += 1
    for y in range(int(page_per_program) * len(program_tables), int(page_file_size) - 1):
            timer += 1
            mem_table.append(Memory(i, nil, 0, 1, 0))
            i += 1
    return mem_table, timer

# argparse "type" to determine if a file exists
def file_exists(filename):
    if not isfile(filename):
        raise argparse.ArgumentTypeError("{} does not exist".format(filename))
    return filename

#function to search the lookup table
def look(prog_num, file_num, prog_tables):
    page_num = 0
    print(prog_num)
    print(file_num)
    for x in range(0, len(prog_tables)):
        if prog_tables[x].prog_num == prog_num and prog_tables[x].file_num == file_num:
            print(1)
            page_num = prog_tables[x].page_num
            break
    print(page_num)
    return page_num

#First in first out algorithm
def fifo(sim, mem_table, timer, page_tables, page_file_size, prog_tables):
    fault = 0
    for x in range(0, 40):
        timer += 1
        in_mem = False
        z = 0
        page_num = 0
        prog_num = sim[x][0]
        file_num = sim[x][1]
        page_num = look(prog_num, file_num, prog_tables)
        #print(page_num)
        for y in range(0, len(mem_table)):
            if prog_num == mem_table[y].prognum and page_num == mem_table[y].page_num:
                in_mem = True
                break
        if not in_mem:
            old = 0 #index of page with lowest time
            clocks = timer
            for z in range(0, len(mem_table)):
                if mem_table[z].clocks < clocks:
                    old = mem_table[z].ind
                    clocks = mem_table[z].clocks
            mem_table[old].prognum = prog_num
            mem_table[old].page_num = page_num
            mem_table[old].clocks = timer
            fault += 1
            #print(fault)
            if paging == 1:
                overflow = False
                if sim[x][1] + 1 > page_tables[sim[x][0]].prog_size:
                    overflow = True
                if not overflow:
                    timer += 1
                    for y in range(0, len(mem_table)):
                        if sim[x][0] == mem_table[y].prognum and sim[x][1] + 1 == mem_table[y].relprogpage:
                            in_mem = True
                            break
                    if not in_mem:
                        old = 0 #index of page with lowest time
                        clocks = timer
                        for z in range(0, len(mem_table)):
                            if mem_table[z].clocks < clocks:
                                old = mem_table[z].ind
                                clocks = mem_table[z].clocks
                        mem_table[old].prognum = sim[x][0]
                        mem_table[old].relprogpage = sim[x][1] + 1
                        mem_table[old].clocks = timer

        #print_mem_table(mem_table)
    return fault
#Clock algorithm
def clock(sim, mem_table, timer, page_tables):
    fault = 0
    for x in range(0, len(sim)):
        timer += 1
        in_mem = False
        for y in range(0, len(mem_table)):
            if sim[x][0] == mem_table[y].prognum and sim[x][1] == mem_table[y].relprogpage:
                in_mem = True
                mem_table[y].usebit = 1
                break
        if not in_mem:
            old = 0 #index of page with lowest time
            clocks = timer
            found = False
            for y in range(0, len(mem_table)):
                if mem_table[y].clocks < clocks:
                    old = mem_table[y].ind
                    clocks = mem_table[y].clocks
            for y in range(old, len(mem_table) - old):
                if mem_table[y].usebit == 0:
                    found = True
                    break
                else:
                    mem_table[y].usebit = 0
            if not found:
                for y in range(0, old):
                    if mem_table[y].usebit == 0:
                        break
                    else:
                        mem_table[y].usebit = 0
            mem_table[old].prognum = sim[x][0]
            mem_table[old].relprogpage = sim[x][1]
            mem_table[old].clocks = timer
            fault += 1
            if paging == 1:
                overflow = False
                if sim[x][1] + 1 > page_tables[sim[x][0]].prog_size:
                    overflow = True
                if not overflow:
                    timer += 1
                    for y in range(0, len(mem_table)):
                        if sim[x][0] == mem_table[y].prognum and sim[x][1] + 1 == mem_table[y].relprogpage:
                            in_mem = True
                            mem_table[y].usebit = 1
                            break
                    if not in_mem:
                        old = 0 #index of page with lowest time
                        clocks = timer
                        found = False
                        for y in range(0, len(mem_table)):
                            if mem_table[y].clocks < clocks:
                                old = mem_table[y].ind
                                clocks = mem_table[y].clocks
                        for y in range(old, len(mem_table) - old):
                            if mem_table[y].usebit == 0:
                                found = True
                                break
                        else:
                            mem_table[y].usebit = 0
                        if not found:
                            for y in range(0, old):
                                if mem_table[y].usebit == 0:
                                    break
                                else:
                                    mem_table[y].usebit = 0
                        mem_table[old].prognum = sim[x][0]
                        mem_table[old].relprogpage = sim[x][1] + 1
                        mem_table[old].clocks = timer
        print_mem_table(mem_table)
    return fault

#Last recently used algorithm
def lru(sim, mem_table, timer, page_tables):
    fault = 0
    for x in range(0, len(sim)):
        timer += 1
        in_mem = False
        for y in range(0, len(mem_table)):
            if sim[x][0] == mem_table[y].prognum and sim[x][1] == mem_table[y].relprogpage:
                mem_table[y].clocks = timer
                in_mem = True
                break
        if not in_mem:
            old = 0 #index of page with lowest time
            clocks = timer
            for y in range(0, len(mem_table)):
                if mem_table[y].clocks < clocks:
                    old = mem_table[y].ind
                    clocks = mem_table[y].clocks
            mem_table[old].prognum = sim[x][0]
            mem_table[old].relprogpage = sim[x][1]
            mem_table[old].clocks = timer
            fault =+ 1
            if paging == 1:
                overflow = False
                if sim[x][1] + 1 > page_tables[sim[x][0]].prog_size:
                    overflow = True
                if not overflow:
                    timer += 1
                    for y in range(0, len(mem_table)):
                        if sim[x][0] == mem_table[y].prognum and sim[x][1] + 1 == mem_table[y].relprogpage:
                            mem_table[y].clocks = timer
                            in_mem = True
                            break
                    if not in_mem:
                        old = 0 #index of page with lowest time
                        clocks = timer
                        for z in range(0, len(mem_table)):
                            if mem_table[z].clocks < clocks:
                                old = mem_table[z].ind
                                clocks = mem_table[z].clocks
                        mem_table[old].prognum = sim[x][0]
                        mem_table[old].relprogpage = sim[x][1] + 1
                        mem_table[old].clocks = timer
        print_mem_table(mem_table)
    return fault

def main():
    

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
    timer = -1
    with open(args.programtrace) as f:
        for line in f:
            if line.strip():# and len(sim) < 10:
                sim.append(line.split())
    
    page_file_size = AVAILABLE_FRAMES / page_size

	#test code for page tables
    page_tables = create_page_tables(programlist, args.page_size)
    #print_page_tables(page_tables, args.page_size)
    
    #test code for prog tables
    prog_tables = create_prog_tables(page_tables)
    #print_prog_tables(prog_tables)

	#test code for the main memory table
    mem_table, timer = create_mem(page_tables, timer, page_file_size)
    #print_mem_table(mem_table)

    fault = fifo(sim, mem_table, timer, page_tables, page_file_size, prog_tables)
    print(fault)

#Print fuctions for testing
def print_page_tables(page_tables, page_size):
    print("{}\t{}\t{}\t{}\t{}".format( "no", "size", "page", "need", "loc"))
    for p in page_tables:
        print("{}\t{}\t{}\t{}\t{} - {}".format(p.prog_no, p.prog_size, page_size, p.pages_needed, p.start_loc, p.end_loc))

def print_prog_tables(page_tables):
    print("\t{}\t{}\t{}".format("program","page", "file"))
    for p in page_tables:
        print("\t{}\t{}\t{}".format(p.prog_num, p.page_num, p.file_num))

def print_mem_table(page_tables):
    print("\t{}\t{}\t{}\t{}\t{}".format("index","program", "page", "usebit", "clocks"))
    for p in page_tables:
        print("\t{}\t{}\t{}\t{}\t{}".format(p.ind, p.prognum, p.page_num, p.usebit, p.clocks))

if __name__ == "__main__":
    main()