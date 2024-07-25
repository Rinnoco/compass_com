import pandas as pd
import re
import argparse
import sys

# Create the size-based mapping
file_sizes = [
    (323, 'measurements_basic.csv'), #T1
    (280, 'measurements_cut_processed.csv'), #T2
    (130, 'battery.csv'), #T3
    (98, 'measurements_meteorology.csv'), #T4
    (87, 'measurements_dust.csv'), #T5
    (32, 'measurements_airquality.csv'), #T6
    (26, 'measurements_oil_detectors.csv'), #T7
    (24, 'measurements_cut_ws.csv'),#T8
    (19, 'location.csv'),
    (8.4, 'measurements_co2.csv'),
    (3.6, 'measurements_buoys_1.csv'),
    (0.049, 'sensors.csv'),
    (0.023, 'microcontrollers_measurements.csv'),
    (0.0067, 'microcontrollers.csv'),
    (0.005, 'station_status.csv'),
    (0.0024, 'measurements.csv'),
    (0.000112, 'measurements_buoys_2.csv')
]

file_sizes.sort(reverse=True, key=lambda x: x[0])
file_mapping = {filename: f"T{i+1}" for i, (_, filename) in enumerate(file_sizes)}

def parse_line(line, pattern):
    match = re.match(pattern, line.strip())
    if match:
        table_name = match.group(1)
        data_type = match.group(2)
        cluster_num = int(match.group(3))
        value = float(match.group(5))
        return table_name, data_type, cluster_num, value
    return None

def process_file(input_file, pattern):
    data_scores = {}
    entropy_scores = {}

    try:
        with open(input_file, 'r') as file:
            for line in file:
                result = parse_line(line, pattern)
                if result:
                    table_name, data_type, cluster_num, value = result

                    if data_type == 'DATA':
                        if table_name not in data_scores:
                            data_scores[table_name] = {}
                        data_scores[table_name][cluster_num] = value
                    elif data_type == 'ENTROPY':
                        if table_name not in entropy_scores:
                            entropy_scores[table_name] = {}
                        entropy_scores[table_name][cluster_num] = value
                else:
                    print(f"Warning: Line did not match pattern and was skipped: {line.strip()}")
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: An unexpected error occurred while processing the file: {e}")
        sys.exit(1)

    return data_scores, entropy_scores

def create_combined_dataframe(data_scores, entropy_scores, file_mapping):
    all_clusters = sorted({num for clusters in data_scores.values() for num in clusters.keys()}.union(
        {num for clusters in entropy_scores.values() for num in clusters.keys()}))

    combined_df = pd.DataFrame(columns=all_clusters)

    for table, clusters in data_scores.items():
        row = {cluster: clusters.get(cluster, -1) for cluster in all_clusters}
        new_table_name = file_mapping.get(table.replace("compass_","").replace(".log","") + ".csv", table) + "_{COMPASS-D}"
        combined_df.loc[new_table_name] = row

    for table, clusters in entropy_scores.items():
        row = {cluster: clusters.get(cluster, -1) for cluster in all_clusters}
        new_table_name = file_mapping.get(table.replace("compass_","").replace(".log","") + ".csv", table) + "_{COMPASS-E}"
        combined_df.loc[new_table_name] = row

    combined_df.columns = [f"{col}" for col in combined_df.columns]
    combined_df.index.name = 'Table'

    # Sort index to group tables by their numeric suffixes
    combined_df = combined_df.reindex(sorted(combined_df.index))

    return combined_df

def main(input_file, output_file):
    pattern = r'^(.+\.log):COMPASS_KMEANS_(DATA|ENTROPY) \((\d+)\): n_clusters = (\d+), the average silhouette_score,([-+]?\d*\.\d+|\d+)$'

    data_scores, entropy_scores = process_file(input_file, pattern)
    combined_df = create_combined_dataframe(data_scores, entropy_scores, file_mapping)

    # Filter tables from T1 to T8
    filtered_combined_df = combined_df[combined_df.index.str.startswith("T1_") |
                                       combined_df.index.str.startswith("T2_") |
                                       combined_df.index.str.startswith("T3_") |
                                       combined_df.index.str.startswith("T4_") |
                                       combined_df.index.str.startswith("T5_") |
                                       combined_df.index.str.startswith("T6_") |
                                       combined_df.index.str.startswith("T7_") |
                                       combined_df.index.str.startswith("T8_")]

    # Count the number of columns with values > 0 for each table
    max_columns_with_values = filtered_combined_df.apply(lambda row: (row > 0).sum(), axis=1).max()

    # Output the result
    print(f"The maximum number of columns with values > 0 for the eight tables is: {max_columns_with_values}")

    filtered_combined_df.T.to_csv(output_file, float_format="%.2f", sep="\t")
    print(f"CSV file '{output_file}' created successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process silhouette scores and output to a CSV file.')
    parser.add_argument('input_file', help='The input file containing silhouette scores')
    parser.add_argument('output_file', help='The output CSV file')
    args = parser.parse_args()

    main(args.input_file, args.output_file)
