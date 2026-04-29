#include <vector>
#include <string>
#include <stdexcept>

namespace pixie {

class DataTable {
private:
    std::vector<std::string> column_names;
    std::vector<std::vector<double>> numeric_data;

public:
    DataTable(const std::vector<std::string>& cols) : column_names(cols) {
        numeric_data.resize(cols.size());
    }

    void add_row(const std::vector<double>& row) {
        if (row.size() != column_names.size()) {
            throw std::invalid_argument("Row size mismatch");
        }
        for (size_t i = 0; i < row.size(); i++) {
            numeric_data[i].push_back(row[i]);
        }
    }
};

} // namespace pixie
