#!/usr/bin/env bash

convert() {
    local dir=$1
    local fit_file=$2

    new_file_name=$(echo $fit_file | sed 's/\.FIT/\.gpx/g')
    file_exists=$(ls ./$dir/$new_file_name 2>&1 > /dev/null)
    if [[ $? != 0 ]]; then
        echo "CREATING ./$dir/$new_file_name"
        gpsbabel -i garmin_fit -o gpx "./$dir/$fit_file" "./$dir/$new_file_name"
    fi
}

#set -x
dirs=( courses rides)
for dir in "${dirs[@]}"; do
    for fit_file in $(ls $dir); do
        if [[ $fit_file == *.FIT ]]; then
            convert $dir $fit_file
        fi
        if [ -d "$dir/$fit_file" ]; then
            new_dir_name="$dir/$fit_file";
            for sublevel_fit_file in $(ls $new_dir_name); do
                if [[ $sublevel_fit_file == *.FIT ]]; then
                    convert $new_dir_name $sublevel_fit_file
                fi
            done
        fi
    done
done
