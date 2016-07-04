#!/usr/bin/env bash

set -x
dirs=( courses rides)
for dir in "${dirs[@]}"; do
    for fit_file in $(ls $dir); do
        if [[ $fit_file == *.FIT ]]; then
            gpsbabel -i garmin_fit -o gpx "./$dir/$fit_file" "./$dir/$(echo $fit_file | sed 's/\.FIT/\.gpx/g')"
        fi
    done
done
