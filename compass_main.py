import os
import tempfile
import zipfile

import pandas as pd
import glob
import sys
import compass_entropy
import compass_recording
import compass_clean_results

from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import silhouette_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OrdinalEncoder


def usage():
    """ Print usage and exit """
    print("Usage: split_files.py <input_file.csv or directory> entropy_file.csv results.csv <num of clusters>")
    sys.exit()


def split_columns(in_file, header, out_file, label, n_clusters, tmp_dir):
    """ Analyze input file, write output file """
    global df
    if os.path.isdir(in_file):
        # Get CSV files list from a folder
        csv_files = glob.glob(in_file + "/*.csv")

        # Read each CSV file into DataFrame
        # This creates a list of dataframes
        df_list = (pd.read_csv(file) for file in csv_files)

        # Concatenate all DataFrames
        df = pd.concat(df_list, ignore_index=True)
    if os.path.isfile(in_file):
        df = pd.read_csv(in_file, sep=',', header=0)
    single_file = f"{tmp_dir}/{os.path.basename(in_file).replace('.csv', '')}_full.csv"
    df.to_csv(single_file, index=False, header=True, mode='a')
    # Define target File name
    split_target_file = f"{tmp_dir}/{os.path.basename(in_file).replace('.csv', '')}_{label}.1.csv"
    split_rest_file = f"{tmp_dir}/{os.path.basename(in_file).replace('.csv', '')}_{label}.2.csv"
    # Write to the file using pandas to_csv
    df.to_csv(split_target_file, index=False, columns=header, header=True, mode='a')
    usecols = list(set(df.columns.tolist()) - set(header))
    compass_recording.compress_and_record_size(split_target_file, split_target_file, label, zipfile.ZIP_DEFLATED,
                                               out_file, 1)
    compass_recording.compress_and_record_size(split_target_file, split_target_file, label, zipfile.ZIP_BZIP2, out_file,
                                               1)
    compass_recording.compress_and_record_size(split_target_file, split_target_file, label, zipfile.ZIP_LZMA, out_file,
                                               1)
    df.to_csv(split_rest_file, index=False, columns=usecols, header=True, mode='a')
    compass_recording.compress_and_record_size(split_rest_file, split_rest_file, label, zipfile.ZIP_DEFLATED, out_file,
                                               2)
    compass_recording.compress_and_record_size(split_rest_file, split_rest_file, label, zipfile.ZIP_BZIP2, out_file, 2)
    compass_recording.compress_and_record_size(split_rest_file, split_rest_file, label, zipfile.ZIP_LZMA, out_file, 2)
    compass_recording.compress_and_record_size(single_file, single_file, label, zipfile.ZIP_DEFLATED, out_file, 0)
    compass_recording.compress_and_record_size(single_file, single_file, label, zipfile.ZIP_BZIP2, out_file, 0)
    compass_recording.compress_and_record_size(single_file, single_file, label, zipfile.ZIP_LZMA, out_file, 0)


# Function : file_compress
# Select the compression mode ZIP_DEFLATED for compression
# or zipfile.ZIP_STORED to just store the file

def split_all(in_file):
    """ Analyse input file, write output file """
    df = pd.read_csv(in_file, sep=',', header=0)
    # Loop through all columns
    for label in df.columns.tolist():
        # Create another sub data frame using the value for the value of the column each time
        df_label = df[label]
        # Define target File name
        split_target_file = f"{in_file.replace('.csv', '')}_{label}.csv"

        # Write to the file using pandas to_csv
        df_label.to_csv(split_target_file, index=False, header=True, mode='a')


def split_column_per_unique_values(df_in, split_source_file, column_chosen):
    # Extract only the columns of the DataFrame
    columns = df_in.columns.values.tolist()

    # Convert Columns into upper case (pandas way of doing it)
    columns_list = list(pd.Series(columns).str.upper())

    # Find the index value of the column
    indx_val = columns_list.index(column_chosen.upper())

    # Take the column to split from the actual column names of data frame
    column_to_split = columns[indx_val]

    # Find unique values from the column
    unique_values = df_in[column_to_split].unique()

    # Loop through all unique values
    for label in unique_values:
        # Create another sub data frame using the value for the value of the column each time
        df_label = df_in[df_in[column_to_split] == label]
        # Define target File name
        split_target_file = f"{split_source_file.replace('.csv', '')}_{label}.csv"

        # Write to the file using pandas to_csv
        df_label.to_csv(split_target_file, index=False, header=True, mode='a')


def preprocess_and_cluster(df_in, n_clusters, label):
    """ Preprocess data and apply KMeans clustering """
    df_processed = df_in.copy()

    # Separate numerical and categorical columns
    numeric_cols = df_processed.select_dtypes(include=['number']).columns
    categorical_cols = df_processed.select_dtypes(include=['object']).columns

    # Create pipelines for numerical and categorical preprocessing
    numeric_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='constant')),  # Impute missing values with constant
        ('scaler', StandardScaler())  # Standardize numerical features
    ])

    categorical_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='constant')),  # Impute missing values with constant
        ('encoder', OrdinalEncoder())  # One-hot encode categorical features
    ])

    # Create column transformer to apply different preprocessing to numerical and categorical columns
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_pipeline, numeric_cols),
            ('cat', categorical_pipeline, categorical_cols)
        ])

    if len(df_processed) <= 0:
        return {}
    # Apply preprocessing pipeline to the transposed DataFrame
    preprocessed = preprocessor.fit_transform(df_processed)

    # Standardize the data
    scaler = StandardScaler()
    processed = scaler.fit_transform(preprocessed.transpose())

    # Apply KMeans clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(processed)

    if len(df_processed.columns) == n_clusters:
        silhouette_avg = 0
        print(f"{label}: n_clusters = {n_clusters}, the average silhouette_score, {silhouette_avg}")
        return clusters
    # Calculate Silhouette Score
    silhouette_avg = silhouette_score(processed, clusters)
    print(f"{label}: n_clusters = {n_clusters}, the average silhouette_score, {silhouette_avg}")

    return clusters


def split_columns_per_entropy_cluster(in_file, out_file, label, n_clusters, tmp_dir):
    """ Analyze input file, write output file """
    df_tmp = pd.read_csv(in_file)
    # Read entropy for each column
    # Read entropy data from CSV file into a DataFrame
    entropies = pd.read_csv(entropy_file)

    # Standardize the data
    scaler = StandardScaler()
    scaled_entropy = scaler.fit_transform(entropies.transpose())

    # Apply KMeans clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(scaled_entropy)

    if len(entropies.columns) <= n_clusters or clusters.min() == clusters.max():
        silhouette_avg = 0
    else:
        silhouette_avg = silhouette_score(scaled_entropy, clusters)
    print(f"{label}: n_clusters = {n_clusters}, the average silhouette_score, {silhouette_avg}")

    # Group column names by cluster
    cluster_groups = {}
    for cluster_idx, col_name in zip(clusters, df_tmp.columns):
        if cluster_idx not in cluster_groups:
            cluster_groups[cluster_idx] = [col_name]
        else:
            cluster_groups[cluster_idx].append(col_name)

    # Write data for each cluster to a single CSV file
    for cluster_idx, columns in cluster_groups.items():
        cluster_df = df_tmp[columns]
        cluster_file = f"{tmp_dir}/{os.path.basename(in_file).replace('.csv', '')}_{label}_cluster_{cluster_idx + 1}.csv"
        cluster_df.to_csv(cluster_file, index=False, header=True)

        # Compress and record size for each compression method
        compass_recording.compress_and_record_size(cluster_file, cluster_file, label, zipfile.ZIP_DEFLATED, out_file,
                                                   cluster_idx + 1)
        compass_recording.compress_and_record_size(cluster_file, cluster_file, label, zipfile.ZIP_BZIP2, out_file,
                                                   cluster_idx + 1)
        compass_recording.compress_and_record_size(cluster_file, cluster_file, label, zipfile.ZIP_LZMA, out_file,
                                                   cluster_idx + 1)


def split_columns_per_cluster(in_file, out_file, label, n_clusters, tmp_dir):
    """ Analyze input file, write output file """
    df_tmp = pd.read_csv(in_file)
    clusters = preprocess_and_cluster(df_tmp, n_clusters, label)

    # Group column names by cluster
    cluster_groups = {}
    for cluster_idx, col_name in zip(clusters, df_tmp.columns):
        if cluster_idx not in cluster_groups:
            cluster_groups[cluster_idx] = [col_name]
        else:
            cluster_groups[cluster_idx].append(col_name)

    # Write data for each cluster to a single CSV file
    for cluster_idx, columns in cluster_groups.items():
        cluster_df = df_tmp[columns]
        cluster_file = f"{tmp_dir}/{os.path.basename(in_file).replace('.csv', '')}_{label}_cluster_{cluster_idx + 1}.csv"
        cluster_df.to_csv(cluster_file, index=False, header=True)
        # Compress and record size for each compression method
        compass_recording.compress_and_record_size(cluster_file, cluster_file, label, zipfile.ZIP_DEFLATED, out_file,
                                                   cluster_idx + 1)
        compass_recording.compress_and_record_size(cluster_file, cluster_file, label, zipfile.ZIP_BZIP2, out_file,
                                                   cluster_idx + 1)
        compass_recording.compress_and_record_size(cluster_file, cluster_file, label, zipfile.ZIP_LZMA, out_file,
                                                   cluster_idx + 1)


def get_entorpy_columns(en_file, entropy):
    edf = pd.read_csv(en_file, sep=',', header=0)
    return edf.columns[(edf < entropy).all()].tolist()


if __name__ == '__main__':
    if len(sys.argv) != 5:
        usage()

    input_file = sys.argv[1]
    entropy_file = sys.argv[2]
    output_file = sys.argv[3]  # results
    num_clusters = int(sys.argv[4])  # Convert string to integer
    print("Splitting {}".format(input_file))

    temp_dir = tempfile.mkdtemp()  # Create temporary directory

    print("Analysing {} and writing {}".format(input_file, entropy_file))
    compass_entropy.analyze(input_file, entropy_file)

    use_columns = get_entorpy_columns(entropy_file, 3)
    if num_clusters == 2:
        split_columns(input_file, use_columns, output_file, "COMPASS_SIBACO", num_clusters, temp_dir)
    split_columns_per_cluster(input_file, output_file, f"COMPASS_KMEANS_DATA ({num_clusters})", num_clusters, temp_dir)
    split_columns_per_entropy_cluster(input_file, output_file, f"COMPASS_KMEANS_ENTROPY ({num_clusters})", num_clusters,
                                      temp_dir)
