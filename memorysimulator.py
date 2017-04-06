#!/usr/bin/env python3

import argparse
from os.path import isfile
from math import ceil
import sys

AVAILABLE_FRAMES = 512

class MemorySimulator:
    def __init__(self, pl_filename, pt_filename, page_size, algorithm, paging):
        with open(pl_filename) as f:
            # index == prog number. filter blank lines
            self.programlist = [int(line.split()[1]) for line in f if line.strip()]

        with open(pt_filename) as f:
            self.programtrace = [tuple(int(i) for i in line.split()) for line in f if line.strip()]

        self.page_size = page_size
        self.algorithm = algorithm
        self.prepaging = bool(paging)
        self.num_frames = int(AVAILABLE_FRAMES / page_size)
        self.programs = []
        self.page_faults = 0
        self.clock_pointer = 0
        self.pc = 0
        self.memory = []

        self.read_programs()
        self.prepare_memory()

    def read_programs(self):
        page_count = 0

        for num, num_pages in enumerate(self.programlist):
            num_pages = ceil(num_pages / self.page_size)
            self.programs.append(Program(num, page_count, num_pages))
            page_count += num_pages

    def prepare_memory(self):
        self.memory = [Page(i) for i in range(self.num_frames)]
        pages_per_program = int(self.num_frames / len(self.programs))

        for i, program in enumerate(self.programs):
            size = 0

            if program.num_pages > pages_per_program:
                size = pages_per_program
            else:
                size = program.num_pages

            for j in range(size):
                main_mem = i * pages_per_program + j
                virt_mem = program.first_page + j

                self.memory[main_mem].update(virt_mem, self.pc, program)

    def run(self):
        print("=" * 24)
        print("Page size:", self.page_size)
        print("Replacement algorithm:", self.algorithm)
        print("Paging policy:", "prepaging" if self.prepaging else "demand")

        for prog_num, word in self.programtrace:
            self.pc += 1
            self.access(self.programs[prog_num], word)

        print("Total page faults:", self.page_faults)
        print("=" * 24)

    def access(self, program, word):
        # convert relative to absolute page number
        word = int(word / self.page_size + program.first_page)

        if word > max(program.jump_table):
            pass
            #return

        if program.jump_table[word] == -1:
            self.page_faults += 1
            self.handle_fault(program, word)
        else:
            self.memory[program.jump_table[word]].access(self.pc)

    def handle_fault(self, program, word, prepage = True):
        sel = 0

        if self.algorithm == "clock":
            while True:
                if self.clock_pointer >= self.num_frames:
                    self.clock_pointer = 0

                if self.memory[self.clock_pointer].clock:
                    self.memory[self.clock_pointer].clock = False
                else:
                    sel = self.clock_pointer
                    break

                self.clock_pointer += 1

            self.clock_pointer += 1
        elif self.algorithm == "lru":
            minimum = self.memory[sel].accessed

            for frame in range(self.num_frames):
                if not minimum:
                    break
                
                if self.memory[frame].accessed < minimum:
                    minimum = self.memory[frame].accessed
                    sel = frame
        elif self.algorithm == "fifo":
            minimum = self.memory[sel].loaded
            
            for frame in range(self.num_frames):
                if not minimum:
                    break

                if self.memory[frame].loaded < minimum:
                    minimum = self.memory[frame].loaded
                    sel = frame

        self.memory[sel].update(word, self.pc, program)

        # choose a page based on this algorithm again if prepaging
        # we flip this to False for a second call so we don't prepage forever
        if self.prepaging and prepage:
            if word == program.num_pages + program.first_page - 1:
                word = program.first_page
            else:
                word += 1

            # is it in memory already?
            if program.jump_table[word] != -1:
                return

            self.handle_fault(program, word, False)

class Program:
    def __init__(self, num, page_num, num_pages):
        self.num = num
        self.first_page = page_num
        self.num_pages = num_pages
        self.jump_table = dict.fromkeys(range(page_num, page_num + num_pages), -1)

class Page:
    def __init__(self, num = None):
        self.num = num
        self.accessed = 1
        self.loaded = 1
        self.contents = 1
        self.owner = None
        self.clock = False

    def update(self, word, pc, program):
        if self.owner:
            self.owner.jump_table[self.contents] = -1

        self.contents = word
        self.owner = program

        program.jump_table[self.contents] = self.num

        self.clock = True
        self.accessed = pc
        self.loaded = pc

    def access(self, pc):
        self.accessed = pc
        self.clock = True

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

    mem_sim = MemorySimulator(args.programlist, args.programtrace, args.page_size, args.algorithm, args.paging)
    mem_sim.run()
