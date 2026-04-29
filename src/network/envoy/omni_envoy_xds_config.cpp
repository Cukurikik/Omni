// OMNI Envoy xDS Config Engine — Network Layer (C++)
// Absorbing envoyproxy/envoy dynamic service routing bounds
// Exact Match and Prefix route distribution geometry

#include <vector>
#include <string>
#include <unordered_map>
#include <algorithm>

template<typename T>
struct EnvoyResult {
    bool ok;
    T value;
    std::string error;
};

struct RouteMatch {
    std::string prefix;
    std::string exact;
    std::string cluster_target;
    int priority;
};

class OmniEnvoyXdsConfig {
private:
    uint64_t routes_evaluated = 0;
    std::vector<RouteMatch> routing_table;

public:
    OmniEnvoyXdsConfig() = default;

    EnvoyResult<bool> register_route(const RouteMatch& route) {
        if (route.cluster_target.empty()) {
            return {false, false, "EnvoyXdsError: Missing target cluster"};
        }
        routing_table.push_back(route);
        // Sort descending by priority so highest priority matches first
        std::sort(routing_table.begin(), routing_table.end(), 
            [](const RouteMatch& a, const RouteMatch& b) {
                return a.priority > b.priority;
            });
        return {true, true, ""};
    }

    EnvoyResult<std::string> resolve_http_path(const std::string& request_path) {
        if (request_path.empty()) {
            return {false, "", "EnvoyXdsError: Empty request path bounds."};
        }

        this->routes_evaluated++;

        for (const auto& route : routing_table) {
            // Check exact match
            if (!route.exact.empty() && request_path == route.exact) {
                return {true, route.cluster_target, ""};
            }
            
            // Check prefix match
            if (!route.prefix.empty()) {
                if (request_path.find(route.prefix) == 0) {
                    return {true, route.cluster_target, ""};
                }
            }
        }

        return {true, "404_NOT_FOUND", ""}; // Envoy exact bounds fallback
    }

    std::unordered_map<std::string, std::string> diagnostics() const {
        return {
            {"engine", "OmniEnvoyXdsConfig"},
            {"evaluations", std::to_string(routes_evaluated)},
            {"active_routes", std::to_string(routing_table.size())},
            {"status", "Operational"}
        };
    }
};
