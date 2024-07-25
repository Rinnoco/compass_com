import os
import csv
import glob
import pandas as pd

from scipy.stats import entropy

def shannon_entropy(col):
    counts = col.value_counts()
    entropy_value = entropy(counts)
    return entropy_value


def analyze(input_file, outfpath):
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
        df = pd.read_csv(input_file, sep=',', header=0)

    entropies = {col: shannon_entropy(df[col]) for col in df}
    # Write output
    with open(outfpath, 'w') as ouf:
        csvwriter = csv.writer(ouf, lineterminator='\n')
        entropy_row = [entropies[colix] for colix in entropies.keys()]
        csvwriter.writerow(entropies)
        csvwriter.writerow(entropy_row)