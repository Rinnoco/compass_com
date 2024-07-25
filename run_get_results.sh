#!/bin/bash
# bash run_get_results.sh results_*.csv

# Create the silhouette results file
grep silhouette *.log> silhouette_results.csv;

# Function to display usage instructions
usage() {
    echo "Usage: $0 [-o OUTPUT_FILE] [--verbose] results_<something>.csv [results_<something_else>.csv ...]" 1>&2
    exit 1
}

# Check if Python is installed
if ! command -v python3 &>/dev/null; then
    echo "Error: Python 3 is required but not found. Please install Python 3." >&2
    exit 1
fi

# Parse command line options
while [[ $# -gt 0 ]]; do
    case $1 in
        -o | --output_file)
            OUTPUT_FILE=$2
            shift
            shift
            ;;
        --verbose | -v)
            VERBOSE="--verbose"
            shift
            ;;
        *)
            INPUT_FILES+=("$1")
            shift
            ;;
    esac
done

# Check if input files are provided
if [[ ${#INPUT_FILES[@]} -eq 0 ]]; then
    echo "Error: No input files provided."
    usage
fi

# Run the Python program for each input file
for input_file in "${INPUT_FILES[@]}"; do
    # Generate output file name based on input file
    output_file="aggregated_${input_file%.csv}.csv"
    # Run the Python program
    python3 compass_clean_results.py "$input_file" -o "$output_file" ${VERBOSE}
    echo "Output stored in: $output_file"
done

