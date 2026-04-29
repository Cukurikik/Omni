#include <vector>
#include <string>
#include <mutex>
#include <memory>

namespace omni {
namespace tonic {

template<typename T, typename E>
struct OmniResult {
    T payload;
    E error;
    bool is_ok;
    
    static OmniResult ok(T val) { return {val, E(), true}; }
    static OmniResult err(E err_msg) { return {T(), err_msg, false}; }
};

class SimulatedDbConnection {
public:
    int id;
    bool in_use;
    SimulatedDbConnection(int _id) : id(_id), in_use(false) {}
};

class TonicDbPool {
private:
    std::vector<std::unique_ptr<SimulatedDbConnection>> connections;
    std::mutex pool_mutex;
    size_t max_connections;

public:
    TonicDbPool(size_t max_conn = 50) : max_connections(max_conn) {
        for(size_t i=0; i<max_conn; ++i) {
            connections.push_back(std::make_unique<SimulatedDbConnection>(i));
        }
    }

    OmniResult<SimulatedDbConnection*, std::string> acquire() {
        std::lock_guard<std::mutex> lock(pool_mutex);
        for (auto& conn : connections) {
            if (!conn->in_use) {
                conn->in_use = true;
                return OmniResult<SimulatedDbConnection*, std::string>::ok(conn.get());
            }
        }
        return OmniResult<SimulatedDbConnection*, std::string>::err("OMNI_POOL_ERR: No available connections in Tonic pool.");
    }

    void release(SimulatedDbConnection* conn) {
        std::lock_guard<std::mutex> lock(pool_mutex);
        if (conn) {
            conn->in_use = false;
        }
    }
};

} // namespace tonic
} // namespace omni
