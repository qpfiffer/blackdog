#!/usr/bin/env bash

dirs=( courses rides)
for dir in "${dirs[@]}"; do
    for fit_file in $(ls $dir); do
        echo $fit_file
    done
done
