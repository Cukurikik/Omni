#include <vector>
#include <cmath>

namespace OmniLab {

struct Vector3 { float x, y, z; };

class PhysicsEngine {
private:
    Vector3 gravity = {0.0f, -9.81f, 0.0f};

public:
    void apply_gravity(Vector3& position, Vector3& velocity, float dt) {
        velocity.y += gravity.y * dt;
        position.x += velocity.x * dt;
        position.y += velocity.y * dt;
        position.z += velocity.z * dt;

        // Ground collision
        if (position.y < 0.0f) {
            position.y = 0.0f;
            velocity.y = 0.0f;
        }
    }
    
    bool check_collision(const Vector3& p1, float r1, const Vector3& p2, float r2) {
        float dx = p1.x - p2.x;
        float dy = p1.y - p2.y;
        float dz = p1.z - p2.z;
        float dist_sq = dx*dx + dy*dy + dz*dz;
        float radii = r1 + r2;
        return dist_sq < (radii * radii);
    }
};

}
