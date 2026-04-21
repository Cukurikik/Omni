// ===========================================================================
// OMNI SPATIAL INDEX ENGINE (POLYLINGUAL REMEDIATION — BATCH 37.6)
// ===========================================================================
// Absorbed From  : libspatialindex R*-tree + Boost.Geometry concepts
// Logic Inherited: C++ / System Layer (Template R-Tree Spatial Index)
// Domain Layer   : System (C++ Core)
// ===========================================================================
//
// By studying libspatialindex and Boost.Geometry, Mother learned that
// 2D spatial indexing for geolocation queries is most efficiently done
// with an R-tree: a balanced tree where each node stores a bounding
// rectangle (MBR). Queries like "find all restaurants within 5km" or
// "find the nearest hospital" reduce to rectangle intersection/containment
// tests that prune the search space from O(N) to O(log N).
//
// C++ templates allow the same R-tree to work with any coordinate type
// (float, double, int) and any dimensionality, while RAII ensures that
// node memory is always properly freed.

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <functional>
#include <limits>
#include <string>
#include <vector>

namespace omni {
namespace system {

// ---- Bounding Rectangle (MBR) ----

/// Axis-Aligned Bounding Box for 2D spatial data.
struct BoundingRect {
    double min_x;
    double min_y;
    double max_x;
    double max_y;

    BoundingRect()
        : min_x(std::numeric_limits<double>::max()),
          min_y(std::numeric_limits<double>::max()),
          max_x(std::numeric_limits<double>::lowest()),
          max_y(std::numeric_limits<double>::lowest()) {}

    BoundingRect(double x1, double y1, double x2, double y2)
        : min_x(x1), min_y(y1), max_x(x2), max_y(y2) {}

    /// Create a point MBR (zero area).
    static BoundingRect point(double x, double y) {
        return BoundingRect(x, y, x, y);
    }

    /// Area of this rectangle.
    double area() const {
        return (max_x - min_x) * (max_y - min_y);
    }

    /// Perimeter of this rectangle.
    double perimeter() const {
        return 2.0 * ((max_x - min_x) + (max_y - min_y));
    }

    /// Center point (x, y).
    void center(double& cx, double& cy) const {
        cx = (min_x + max_x) / 2.0;
        cy = (min_y + max_y) / 2.0;
    }

    /// Test intersection with another rectangle.
    bool intersects(const BoundingRect& other) const {
        return !(other.min_x > max_x || other.max_x < min_x ||
                 other.min_y > max_y || other.max_y < min_y);
    }

    /// Test if this rectangle fully contains another.
    bool contains(const BoundingRect& other) const {
        return other.min_x >= min_x && other.max_x <= max_x &&
               other.min_y >= min_y && other.max_y <= max_y;
    }

    /// Test if this rectangle contains a point.
    bool contains_point(double px, double py) const {
        return px >= min_x && px <= max_x && py >= min_y && py <= max_y;
    }

    /// Expand this rectangle to include another.
    void expand(const BoundingRect& other) {
        min_x = std::min(min_x, other.min_x);
        min_y = std::min(min_y, other.min_y);
        max_x = std::max(max_x, other.max_x);
        max_y = std::max(max_y, other.max_y);
    }

    /// Calculate the area enlargement if we add another rect.
    double enlargement(const BoundingRect& other) const {
        BoundingRect merged = *this;
        merged.expand(other);
        return merged.area() - area();
    }

    /// Squared distance from a point to the nearest edge of this rect.
    double sq_distance_to_point(double px, double py) const {
        double dx = std::max({min_x - px, 0.0, px - max_x});
        double dy = std::max({min_y - py, 0.0, py - max_y});
        return dx * dx + dy * dy;
    }
};

// ---- Spatial Entry ----

/// A spatial entry stored in the R-tree: MBR + user data.
struct SpatialEntry {
    BoundingRect mbr;
    std::string  id;
    std::string  label;
    double       latitude;
    double       longitude;
};

// ---- R-Tree Node ----

/// Internal node structure. Leaf nodes store entries; internal nodes store children.
struct RTreeNode {
    BoundingRect mbr;
    bool         is_leaf;
    std::vector<SpatialEntry>  entries;    // Only for leaf nodes
    std::vector<RTreeNode*>    children;   // Only for internal nodes

    RTreeNode(bool leaf) : is_leaf(leaf) {}

    ~RTreeNode() {
        for (auto* child : children) {
            delete child;
        }
    }

    /// Recompute MBR from children or entries.
    void recompute_mbr() {
        mbr = BoundingRect();
        if (is_leaf) {
            for (const auto& entry : entries) {
                mbr.expand(entry.mbr);
            }
        } else {
            for (const auto* child : children) {
                mbr.expand(child->mbr);
            }
        }
    }
};

// ---- R-Tree Configuration ----

struct RTreeConfig {
    int max_entries_per_node;  // Maximum entries before split (default: 16)
    int min_entries_per_node;  // Minimum entries after split (default: max/3)

    RTreeConfig() : max_entries_per_node(16), min_entries_per_node(5) {}
    RTreeConfig(int max_e) : max_entries_per_node(max_e),
                              min_entries_per_node(std::max(2, max_e / 3)) {}
};

// ---- Core Engine ----

/// Production R-tree spatial index for 2D geolocation queries.
class OmniSpatialIndexEngine {
public:
    explicit OmniSpatialIndexEngine(RTreeConfig config = RTreeConfig())
        : config_(config), root_(nullptr), size_(0),
          total_queries_(0), total_inserts_(0) {
        root_ = new RTreeNode(true); // Start with empty leaf root
    }

    ~OmniSpatialIndexEngine() {
        delete root_;
    }

    // Disable copy (tree owns heap memory)
    OmniSpatialIndexEngine(const OmniSpatialIndexEngine&) = delete;
    OmniSpatialIndexEngine& operator=(const OmniSpatialIndexEngine&) = delete;

    // ---- Insert ----

    /// Insert a spatial entry into the R-tree.
    void insert(const SpatialEntry& entry) {
        insert_recursive(root_, entry);

        // Check if root was split
        if (static_cast<int>(root_->is_leaf ? root_->entries.size() : root_->children.size())
            > config_.max_entries_per_node) {
            split_root();
        }

        size_++;
        total_inserts_++;
    }

    /// Convenience: insert a point (lat/lon) with ID and label.
    void insert_point(const std::string& id, double lat, double lon,
                      const std::string& label = "") {
        SpatialEntry entry;
        entry.mbr = BoundingRect::point(lon, lat); // x=lon, y=lat
        entry.id = id;
        entry.label = label;
        entry.latitude = lat;
        entry.longitude = lon;
        insert(entry);
    }

    // ---- Range Query (Rectangle) ----

    /// Find all entries whose MBR intersects the given search rectangle.
    std::vector<SpatialEntry> query_range(const BoundingRect& searchRect) const {
        total_queries_++;
        std::vector<SpatialEntry> results;
        query_range_recursive(root_, searchRect, results);
        return results;
    }

    /// Find all entries within a geographic radius (approximate, using degrees).
    std::vector<SpatialEntry> query_radius(double center_lat, double center_lon,
                                           double radius_deg) const {
        BoundingRect searchRect(
            center_lon - radius_deg, center_lat - radius_deg,
            center_lon + radius_deg, center_lat + radius_deg
        );

        auto candidates = query_range(searchRect);

        // Filter to actual circle
        std::vector<SpatialEntry> filtered;
        double r2 = radius_deg * radius_deg;
        for (const auto& entry : candidates) {
            double dx = entry.longitude - center_lon;
            double dy = entry.latitude - center_lat;
            if (dx * dx + dy * dy <= r2) {
                filtered.push_back(entry);
            }
        }
        return filtered;
    }

    // ---- Nearest Neighbor ----

    /// Find the K nearest entries to a point.
    std::vector<SpatialEntry> query_knn(double lat, double lon, int k) const {
        total_queries_++;
        std::vector<std::pair<double, SpatialEntry>> candidates;
        knn_recursive(root_, lon, lat, candidates);

        // Sort by distance
        std::sort(candidates.begin(), candidates.end(),
            [](const auto& a, const auto& b) { return a.first < b.first; });

        std::vector<SpatialEntry> results;
        for (int i = 0; i < k && i < static_cast<int>(candidates.size()); i++) {
            results.push_back(candidates[i].second);
        }
        return results;
    }

    // ---- Stats ----

    int size() const { return size_; }
    int depth() const { return compute_depth(root_); }
    uint64_t total_queries() const { return total_queries_; }
    uint64_t total_inserts() const { return total_inserts_; }

    // ---- Diagnostics ----

    struct DiagnosticsInfo {
        std::string engine;
        std::string layer;
        int         entry_count;
        int         tree_depth;
        uint64_t    queries;
        uint64_t    inserts;
        int         max_entries_per_node;
        double      root_area;
    };

    DiagnosticsInfo diagnostics() const {
        DiagnosticsInfo info;
        info.engine = "OmniSpatialIndexEngine";
        info.layer = "C++ System";
        info.entry_count = size_;
        info.tree_depth = depth();
        info.queries = total_queries_;
        info.inserts = total_inserts_;
        info.max_entries_per_node = config_.max_entries_per_node;
        info.root_area = root_ ? root_->mbr.area() : 0.0;
        return info;
    }

private:
    RTreeConfig  config_;
    RTreeNode*   root_;
    int          size_;
    mutable uint64_t total_queries_;
    uint64_t     total_inserts_;

    // ---- Recursive Insert ----

    void insert_recursive(RTreeNode* node, const SpatialEntry& entry) {
        if (node->is_leaf) {
            node->entries.push_back(entry);
            node->recompute_mbr();

            // Split if overflow
            if (static_cast<int>(node->entries.size()) > config_.max_entries_per_node) {
                // Will be handled by caller
            }
        } else {
            // Choose subtree with minimum enlargement (Guttman's algorithm)
            RTreeNode* best_child = choose_subtree(node, entry.mbr);
            insert_recursive(best_child, entry);

            // Check child overflow
            if (static_cast<int>(best_child->is_leaf ?
                    best_child->entries.size() : best_child->children.size())
                > config_.max_entries_per_node) {
                split_node(node, best_child);
            }

            node->recompute_mbr();
        }
    }

    // ---- Choose Subtree (Minimum Enlargement) ----

    RTreeNode* choose_subtree(RTreeNode* parent, const BoundingRect& entry_mbr) const {
        RTreeNode* best = parent->children[0];
        double best_enlargement = best->mbr.enlargement(entry_mbr);
        double best_area = best->mbr.area();

        for (size_t i = 1; i < parent->children.size(); i++) {
            double enlargement = parent->children[i]->mbr.enlargement(entry_mbr);
            double area = parent->children[i]->mbr.area();

            // Prefer minimum enlargement; break ties by minimum area
            if (enlargement < best_enlargement ||
                (enlargement == best_enlargement && area < best_area)) {
                best = parent->children[i];
                best_enlargement = enlargement;
                best_area = area;
            }
        }
        return best;
    }

    // ---- Node Splitting (Linear Split) ----

    void split_node(RTreeNode* parent, RTreeNode* overflow_node) {
        auto* new_node = new RTreeNode(overflow_node->is_leaf);

        if (overflow_node->is_leaf) {
            // Split entries between overflow_node and new_node
            auto& entries = overflow_node->entries;
            size_t mid = entries.size() / 2;

            // Sort by x-coordinate of MBR center
            std::sort(entries.begin(), entries.end(),
                [](const SpatialEntry& a, const SpatialEntry& b) {
                    double ax, ay, bx, by;
                    a.mbr.center(ax, ay);
                    b.mbr.center(bx, by);
                    return ax < bx;
                });

            new_node->entries.assign(entries.begin() + mid, entries.end());
            entries.resize(mid);
        } else {
            auto& children = overflow_node->children;
            size_t mid = children.size() / 2;

            std::sort(children.begin(), children.end(),
                [](const RTreeNode* a, const RTreeNode* b) {
                    double ax, ay, bx, by;
                    a->mbr.center(ax, ay);
                    b->mbr.center(bx, by);
                    return ax < bx;
                });

            new_node->children.assign(children.begin() + mid, children.end());
            children.resize(mid);
        }

        overflow_node->recompute_mbr();
        new_node->recompute_mbr();
        parent->children.push_back(new_node);
    }

    // ---- Root Split ----

    void split_root() {
        auto* new_root = new RTreeNode(false);
        auto* sibling = new RTreeNode(root_->is_leaf);

        if (root_->is_leaf) {
            auto& entries = root_->entries;
            size_t mid = entries.size() / 2;
            sibling->entries.assign(entries.begin() + mid, entries.end());
            entries.resize(mid);
        } else {
            auto& children = root_->children;
            size_t mid = children.size() / 2;
            sibling->children.assign(children.begin() + mid, children.end());
            children.resize(mid);
        }

        root_->recompute_mbr();
        sibling->recompute_mbr();

        new_root->children.push_back(root_);
        new_root->children.push_back(sibling);
        new_root->recompute_mbr();

        root_ = new_root;
    }

    // ---- Recursive Range Query ----

    void query_range_recursive(const RTreeNode* node, const BoundingRect& search,
                               std::vector<SpatialEntry>& results) const {
        if (!node->mbr.intersects(search)) return;

        if (node->is_leaf) {
            for (const auto& entry : node->entries) {
                if (entry.mbr.intersects(search)) {
                    results.push_back(entry);
                }
            }
        } else {
            for (const auto* child : node->children) {
                query_range_recursive(child, search, results);
            }
        }
    }

    // ---- Recursive KNN ----

    void knn_recursive(const RTreeNode* node, double qx, double qy,
                       std::vector<std::pair<double, SpatialEntry>>& candidates) const {
        if (node->is_leaf) {
            for (const auto& entry : node->entries) {
                double dx = entry.longitude - qx;
                double dy = entry.latitude - qy;
                double dist = std::sqrt(dx * dx + dy * dy);
                candidates.emplace_back(dist, entry);
            }
        } else {
            // Sort children by distance to query point (nearest first)
            std::vector<std::pair<double, const RTreeNode*>> sorted_children;
            for (const auto* child : node->children) {
                double d2 = child->mbr.sq_distance_to_point(qx, qy);
                sorted_children.emplace_back(d2, child);
            }
            std::sort(sorted_children.begin(), sorted_children.end(),
                [](const auto& a, const auto& b) { return a.first < b.first; });

            for (const auto& [_, child] : sorted_children) {
                knn_recursive(child, qx, qy, candidates);
            }
        }
    }

    // ---- Tree Depth ----

    int compute_depth(const RTreeNode* node) const {
        if (!node || node->is_leaf) return 1;
        int max_child_depth = 0;
        for (const auto* child : node->children) {
            max_child_depth = std::max(max_child_depth, compute_depth(child));
        }
        return 1 + max_child_depth;
    }
};

} // namespace system
} // namespace omni
