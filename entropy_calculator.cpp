#include <iostream>
#include <fstream>
#include <unordered_map>
#include <vector>
#include <cmath>
#include <sstream>

std::unordered_map<std::string, double> compute_entropy(const std::string& file_path) {
    std::ifstream file(file_path);
    if (!file.is_open()) {
        std::cerr << "Error: Could not open file " << file_path << std::endl;
        exit(1);
    }

    std::unordered_map<std::string, std::unordered_map<std::string, int>> column_counts;
    std::vector<std::string> column_names;
    std::string line;

    // Read header
    if (std::getline(file, line)) {
        std::stringstream ss(line);
        std::string column;
        while (std::getline(ss, column, ',')) {
            column_names.push_back(column);
            column_counts[column] = {};
        }
    }

    // Read data
    while (std::getline(file, line)) {
        std::stringstream ss(line);
        std::string value;
        int col_index = 0;
        while (std::getline(ss, value, ',')) {
            column_counts[column_names[col_index]][value]++;
            col_index++;
        }
    }

    file.close();

    // Compute entropy for each column
    std::unordered_map<std::string, double> entropy_values;
    for (const auto& col : column_counts) {
        double entropy = 0.0;
        int total = 0;
        for (const auto& val : col.second) {
            total += val.second;
        }
        for (const auto& val : col.second) {
            double p = static_cast<double>(val.second) / total;
            entropy -= p * std::log2(p);
        }
        entropy_values[col.first] = entropy;
    }

    return entropy_values;
}

int main(int argc, char* argv[]) {
    if (argc != 3) {
        std::cerr << "Usage: " << argv[0] << " <input_csv> <output_csv>" << std::endl;
        return 1;
    }

    std::string input_file = argv[1];
    std::string output_file = argv[2];

    std::unordered_map<std::string, double> entropies = compute_entropy(input_file);

    std::ofstream out(output_file);
    if (!out.is_open()) {
        std::cerr << "Error: Could not open output file " << output_file << std::endl;
        return 1;
    }

    for (const auto& e : entropies) {
        out << e.first << "," << e.second << std::endl;
    }

    out.close();
    std::cout << "Entropy values saved to " << output_file << std::endl;
    return 0;
}
