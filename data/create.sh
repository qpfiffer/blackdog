#!/usr/bin/env bash

#set -x
dirs=( courses rides)
for dir in "${dirs[@]}"; do
    for fit_file in $(ls $dir); do
        if [[ $fit_file == *.FIT ]]; then
            new_file_name=$(echo $fit_file | sed 's/\.FIT/\.gpx/g')
            file_exists=$(ls ./$dir/$new_file_name 2>&1 > /dev/null)
            if [[ $? != 0 ]]; then
                echo "CREATING ./$dir/$new_file_name"
                gpsbabel -i garmin_fit -o gpx "./$dir/$fit_file" "./$dir/$new_file_name"
            fi
        fi
    done
done
