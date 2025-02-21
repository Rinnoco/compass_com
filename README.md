# COMPASS Project

## Description

The COMPASS (Compression and Access with Significantly Reduced Spaces) dataset supports research and development efforts
aimed at optimizing big data storage and retrieval. This includes various data files processed through the COMPASS tool
to demonstrate and evaluate our signature-based compression techniques designed to minimize storage and I/O costs, while
enhancing data fidelity and retrieval efficiency for ICT services.

## Content

The dataset contains:

- **CSV Files**: Raw and processed data files in CSV format used to validate the COMPASS compression algorithms.
- **Entropy Data**: Results of entropy calculations that assess the randomness and complexity of the data.
- **Compression Results**: Detailed outcomes of different compression strategies applied to the dataset.
- **Silhouette Scores**: Evaluative scores for the clustering methods utilized in the data compression process.

## Usage

This dataset is ideal for researchers and technologists focusing on data compression methods, especially those seeking
to improve big data management within ICT applications. Users can replicate COMPASS compression techniques on these data
files to analyze performance in varied environments.

## Steps to Utilize the Dataset

1. **Initial Processing**:
   Run the `run_compass_for_all.sh` script to process all CSV files within the designated directory. This script applies
   the COMPASS tool to compute entropy and prepare data for compression.
   ```bash
   bash run_compass_for_all.sh
   ```

2. **Result Aggregation**:
   After processing, execute the `run_get_results.sh` script to aggregate initial results from the processing scripts.
   ```bash
   bash run_get_results.sh
   ```

3. **Data Cleaning and Analysis**:
   Use the Python scripts `compass_clean_results.py` and `compass_clean_silhouette_scores.py` to clean up the results
   and calculate silhouette scores for the data clusters.
   ```bash
   python3 compass_clean_results.py [options]
   python3 compass_clean_silhouette_scores.py [input_file] [output_file]
   ```

## How to Download

To download the dataset:

1. Visit the [COMPASS Project page](#https://rinnoco.com/projects/compass.html).
2. Go to Zenodo and Click on the "Download" button for the files you are interested in.

## Citation

When using this dataset for research, please cite it as follows:

```
Costa, C., Chrysanthis, P., Herodotou, H., Costa, M., Stavrakis, E., & Nicolaou, N. (2025). COMPASS: Big Data Compression Tool using Attribute-based Signatures. Zenodo. https://doi.org/10.5281/zenodo.14759015
```

## License

This dataset is available under
the [Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0), which
permits sharing and adapting the material provided that appropriate credit is given.

## Contact Information

For queries about the dataset or the COMPASS project, contact Dr. Constntinos Costa at costa.c@rinnoco.com.

## Acknowledgments

This work is implemented under the programme of social cohesion “THALIA 2021-2027” co-funded by the European Union,
through Research and Innovation Foundation, under project COMPASS - CONCEPT/0823/0002, and is also partially supported
by the European Union’s Horizon Europe program for Research and Innovation through the HYPER-AI project under Grant No. 101135982. The views, findings, conclusions, or recommendations expressed in this material are solely those of the
author(s) and do not necessarily represent those of the sponsors.
