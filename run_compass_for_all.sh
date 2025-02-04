#!/bin/bash

# Loop through each CSV file in the envmondb directory
for file in envmondb/*.csv; do
    # Extract filename without extension
    filename=$(basename "$file" .csv)
    
    # Get the number of columns by counting commas in the first row
    num_columns=$(head -n 1 "$file" | tr -cd ',' | wc -c)
    ((num_columns++))  # Add 1 to include the last column
    # Run the command for each file
    ./run_compass_experiments.sh "$file" "entropy_${filename}_file.csv" "results_${filename}.csv" "$num_columns" &> "compass_${filename}.log"
done
