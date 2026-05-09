/// @omni-layer System | @omni-source desaixie/zeroverse | @omni-lang C++
/// @omni-description Mesh decimation kernel: edge-collapse based mesh
/// simplification with quadric error metrics for LOD generation.
#include <cmath>
#include <vector>
#include <algorithm>

namespace omni { namespace mesh {

struct Vertex { float x, y, z; };
struct Triangle { int v0, v1, v2; };

struct QuadricError {
    double matrix[10] = {};  // symmetric 4x4 stored as upper triangle

    void add(const QuadricError& other) {
        for (int i = 0; i < 10; i++) matrix[i] += other.matrix[i];
    }

    double evaluate(float x, float y, float z) const {
        // Q(v) = v^T * A * v + 2 * b^T * v + c
        double result = matrix[0]*x*x + 2*matrix[1]*x*y + 2*matrix[2]*x*z + 2*matrix[3]*x
                       + matrix[4]*y*y + 2*matrix[5]*y*z + 2*matrix[6]*y
                       + matrix[7]*z*z + 2*matrix[8]*z + matrix[9];
        return result;
    }
};

class MeshDecimator {
    std::vector<Vertex> vertices_;
    std::vector<Triangle> triangles_;
    std::vector<QuadricError> quadrics_;

    static QuadricError compute_plane_quadric(const Vertex& v0, const Vertex& v1, const Vertex& v2) {
        float nx = (v1.y-v0.y)*(v2.z-v0.z) - (v1.z-v0.z)*(v2.y-v0.y);
        float ny = (v1.z-v0.z)*(v2.x-v0.x) - (v1.x-v0.x)*(v2.z-v0.z);
        float nz = (v1.x-v0.x)*(v2.y-v0.y) - (v1.y-v0.y)*(v2.x-v0.x);
        float len = std::sqrt(nx*nx + ny*ny + nz*nz);
        if (len > 1e-8f) { nx /= len; ny /= len; nz /= len; }
        float d = -(nx*v0.x + ny*v0.y + nz*v0.z);
        QuadricError q;
        q.matrix[0] = nx*nx; q.matrix[1] = nx*ny; q.matrix[2] = nx*nz; q.matrix[3] = nx*d;
        q.matrix[4] = ny*ny; q.matrix[5] = ny*nz; q.matrix[6] = ny*d;
        q.matrix[7] = nz*nz; q.matrix[8] = nz*d;
        q.matrix[9] = d*d;
        return q;
    }

public:
    MeshDecimator(const std::vector<Vertex>& verts, const std::vector<Triangle>& tris)
        : vertices_(verts), triangles_(tris), quadrics_(verts.size()) {
        for (const auto& tri : triangles_) {
            auto q = compute_plane_quadric(vertices_[tri.v0], vertices_[tri.v1], vertices_[tri.v2]);
            quadrics_[tri.v0].add(q);
            quadrics_[tri.v1].add(q);
            quadrics_[tri.v2].add(q);
        }
    }

    double edge_collapse_cost(int v0, int v1) const {
        QuadricError combined;
        combined.add(quadrics_[v0]);
        combined.add(quadrics_[v1]);
        float mx = (vertices_[v0].x + vertices_[v1].x) * 0.5f;
        float my = (vertices_[v0].y + vertices_[v1].y) * 0.5f;
        float mz = (vertices_[v0].z + vertices_[v1].z) * 0.5f;
        return combined.evaluate(mx, my, mz);
    }

    int decimate(int target_triangles) {
        int removed = 0;
        while (static_cast<int>(triangles_.size()) - removed > target_triangles && !triangles_.empty()) {
            // Find cheapest edge collapse (simplified)
            double min_cost = 1e30;
            int best_tri = 0;
            for (size_t i = 0; i < triangles_.size(); i++) {
                double c01 = edge_collapse_cost(triangles_[i].v0, triangles_[i].v1);
                if (c01 < min_cost) { min_cost = c01; best_tri = static_cast<int>(i); }
            }
            triangles_.erase(triangles_.begin() + best_tri);
            removed++;
        }
        return static_cast<int>(triangles_.size());
    }

    int vertex_count() const { return static_cast<int>(vertices_.size()); }
    int triangle_count() const { return static_cast<int>(triangles_.size()); }
};

}} // namespace omni::mesh
