#!/bin/sh

for i in 0 1
do
    for algo in lru clock fifo
    do
        for page_size in 1 2 4 8 16
        do
            ./memorysimulator.py programlist.txt programtrace.txt $page_size $algo $i
            echo
        done
    done
done
