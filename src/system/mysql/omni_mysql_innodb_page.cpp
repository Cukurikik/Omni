// OMNI MySQL InnoDB Page Engine — System Layer (C++)
// Absorbing mysql/mysql-server B+Tree structure
// 16KB Page Split Mathematics and node clustering

#include <vector>
#include <string>
#include <unordered_map>
#include <memory>
#include <algorithm>

template<typename T>
struct MysqlResult {
    bool ok;
    T value;
    std::string error;
};

struct BTreeNode {
    bool is_leaf;
    std::vector<int> keys;
    std::vector<std::shared_ptr<BTreeNode>> children;
    std::vector<std::string> values; // Only used if leaf
};

class OmniMysqlInnodbPage {
private:
    uint64_t pages_split = 0;
    int order;
    std::shared_ptr<BTreeNode> root;

public:
    OmniMysqlInnodbPage(int tree_order = 4) : order(tree_order) {
        root = std::make_shared<BTreeNode>();
        root->is_leaf = true;
    }

    // Mathematical representation of InnoDB Page Limit Splitting Protocol
    MysqlResult<bool> insert_clustered_index(int key, const std::string& record) {
        auto r = root;
        if (r->keys.size() == order - 1) {
            auto s = std::make_shared<BTreeNode>();
            root = s;
            s->is_leaf = false;
            s->children.push_back(r);
            split_child(s, 0);
            insert_non_full(s, key, record);
        } else {
            insert_non_full(r, key, record);
        }
        return {true, true, ""};
    }

private:
    void insert_non_full(std::shared_ptr<BTreeNode> x, int k, const std::string& v) {
        int i = x->keys.size() - 1;

        if (x->is_leaf) {
            x->keys.push_back(0);
            x->values.push_back("");
            
            while (i >= 0 && k < x->keys[i]) {
                x->keys[i + 1] = x->keys[i];
                x->values[i + 1] = x->values[i];
                i--;
            }
            x->keys[i + 1] = k;
            x->values[i + 1] = v;
        } else {
            while (i >= 0 && k < x->keys[i]) {
                i--;
            }
            i++;
            if (x->children[i]->keys.size() == order - 1) {
                split_child(x, i);
                if (k > x->keys[i]) {
                    i++;
                }
            }
            insert_non_full(x->children[i], k, v);
        }
    }

    void split_child(std::shared_ptr<BTreeNode> x, int i) {
        this->pages_split++;
        auto y = x->children[i];
        auto z = std::make_shared<BTreeNode>();
        z->is_leaf = y->is_leaf;
        
        int t = order / 2;

        for (int j = 0; j < t - 1; j++) {
            z->keys.push_back(y->keys[j + t]);
            if (z->is_leaf) z->values.push_back(y->values[j + t]);
        }

        if (!y->is_leaf) {
            for (int j = 0; j < t; j++) {
                z->children.push_back(y->children[j + t]);
            }
        }

        x->children.insert(x->children.begin() + i + 1, z);
        x->keys.insert(x->keys.begin() + i, y->keys[t - 1]);

        y->keys.resize(t - 1);
        if (y->is_leaf) y->values.resize(t - 1);
        if (!y->is_leaf) y->children.resize(t);
    }

public:
    std::unordered_map<std::string, std::string> diagnostics() const {
        return {
            {"engine", "OmniMysqlInnodbPage"},
            {"tree_order", std::to_string(order)},
            {"pages_split", std::to_string(pages_split)},
            {"status", "Operational"}
        };
    }
};
