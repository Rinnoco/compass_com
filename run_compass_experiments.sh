#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -ne 4 ]; then
    echo "Usage: $0 <input_file.csv or directory> entropy_file.csv results.csv <num of clusters>"
    exit 1
fi

# Extract arguments
input_file="$1"
entropy_file="$2"
results_file="$3"
num_clusters="$4"

# Check if the input file/directory exists
if [ ! -f "$input_file" ] && [ ! -d "$input_file" ]; then
    echo "Error: Input file/directory '$input_file' not found."
    exit 1
fi

python3 sibaco_entropy.py "$input_file" "$entropy_file"

# Iterate over cluster sizes from 2 to 16
for ((i=2; i<=num_clusters; i++)); do
    echo "Running program for cluster size $i..."
    python3 compass_main.py "$input_file" "$entropy_file" "$results_file" "$i"
done

echo "Program execution complete."

