import csv
from collections import defaultdict
import argparse
import sys


def parse_arguments():
    parser = argparse.ArgumentParser(description='Aggregate data from input files.')
    parser.add_argument('input_files', nargs='+', help='Input CSV files')
    parser.add_argument('--output_file', '-o', default='aggregated_data.csv', help='Output CSV file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Print verbose output')
    return parser.parse_args()


def aggregate_data(input_files, output_file, verbose=False):
    # Initialize data structures
    data = defaultdict(lambda: {"size": 0, "num_clusters": "Unknown"})
    baseline_data = defaultdict(int)
    method_compression_size = defaultdict(list)

    # Parse input data from each file
    for input_file in input_files:
        with open(input_file, newline='') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip the header row
            for row in reader:
                row = [item.strip() for item in row]  # Strip whitespace from each item
                if len(row) < 6:
                    if verbose:
                        print(f"Ignoring invalid row: {row}")
                    continue
                cluster, file_name, method, compression, size, _ = row
                size = int(size) if size.isdigit() else 0
                if "full" in file_name:
                    baseline_data[method + "_" + compression] += size
                else:
                    method_parts = method.split(" (")
                    num_clusters = method_parts[1].replace(')', '') if len(method_parts) > 1 else "2"
                    data[method + "_" + compression]["size"] += size
                    data[method + "_" + compression]["num_clusters"] = num_clusters
                    method_compression_size[method].append((cluster, size, compression))

    # Write aggregated data to the output file
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Method-Compression', 'Number of Clusters', 'Sum of Size (bytes)', 'Performance'])

        if verbose:
            # Write aggregated data
            for method_compression, values in data.items():
                writer.writerow([method_compression, values["num_clusters"], values["size"],0])

            # Write baseline data
            for method_compression, size in baseline_data.items():
                writer.writerow(["BASELINE_" + method_compression, 1, size])
            writer.writerow("-----")
        min_baseline = min(baseline_data.values())
        writer.writerow(["COMPASS_BASELINE", 1, min_baseline,0])
        # Calculate and write COMPASS row for each method
        for method, cluster_sizes in method_compression_size.items():
            cluster_dict = defaultdict(list)

            # Store sizes in the dictionary based on clusters
            for cluster, size, _ in cluster_sizes:
                cluster_dict[cluster].append(size)

            # Find the minimum size for each cluster and sum them up
            total_min_size = sum(min(sizes, default=0) for sizes in cluster_dict.values())
            writer.writerow(
                [f"COMPASS_{method}", len(cluster_dict), total_min_size,
                 ((min_baseline - total_min_size) / min_baseline)])

    print(f"Aggregated data CSV file '{output_file}' created successfully.")


def main():
    args = parse_arguments()

    # Check if at least one input file is provided
    if not args.input_files:
        print("At least one input file must be provided.")
        sys.exit(1)

    aggregate_data(args.input_files, args.output_file, args.verbose)


if __name__ == "__main__":
    main()
