"""
sibaco_entropy.py
Author: Constantinos Costa
Purpose: This script reads a CSV file and generates the Shannon's entropy for each column
"""

import csv
import glob
import os

from scipy.stats import entropy
import sys
import pandas as pd
import subprocess


def usage():
    """ Print usage and exit """
    print("Usage: sibaco_entropy.py input_file.csv results.csv")
    sys.exit()


def shannon_entropy(col):
    counts = col.value_counts()
    entropy_value = entropy(counts)
    return entropy_value


def analyze(infpath, outfpath):
    """ Analyse input file, write output file """
    df = []
    if os.path.isdir(input_file):
        # Get CSV files list from a folder
        csv_files = glob.glob(input_file + "/*.csv")

        # Read each CSV file into DataFrame
        # This creates a list of dataframes
        df_list = (pd.read_csv(file) for file in csv_files)

        # Concatenate all DataFrames
        df = pd.concat(df_list, ignore_index=True)
    if os.path.isfile(input_file):
        df = pd.read_csv(infpath, sep=',', header=0)

    entropies = {col: shannon_entropy(df[col]) for col in df}
    # Write output
    with open(outfpath, 'w') as ouf:
        csvwriter = csv.writer(ouf, lineterminator='\n')
        entropy_row = [entropies[colix] for colix in entropies.keys()]
        csvwriter.writerow(entropies)
        csvwriter.writerow(entropy_row)


def analyze_C(input_file, outfpath):
    """ Call the C++ entropy calculator """
    cpp_executable = "./entropy_calculator"  # Ensure the compiled C++ executable is present
    try:
        subprocess.run([cpp_executable, input_file, outfpath], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running entropy calculator: {e}")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        usage()
    input_file, output_file = sys.argv[1], sys.argv[2]
    print("Analysing {} and writing {}".format(input_file, output_file))
    analyze(input_file, output_file)
