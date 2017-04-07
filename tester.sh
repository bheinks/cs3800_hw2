#!/usr/bin/bash

algos=(lru clock fifo)

for i in {0..1}
do
    for algo in "${algos[@]}"
    do
        for page_size in 1 2 4 8 16
        do
            ./memorysimulator.py programlist.txt programtrace.txt $page_size $algo $i
            echo
        done
    done
done
